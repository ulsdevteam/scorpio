from elasticsearch_dsl import connections
from elasticsearch.helpers import streaming_bulk
from rac_es.documents import Agent, Collection, Object, Term

from .models import DataObject

from scorpio import settings

TYPES = {
    "agent": Agent,
    "collection": Collection,
    "object": Object,
    "term": Term
}


class IndexError(Exception): pass


class Indexer:

    def __init__(self):
        self.connection = connections.create_connection(hosts=settings.ELASTICSEARCH['default']['hosts'], timeout=60)

    def prepare_data(self, type, data):
        doc = TYPES[type](**data.data)
        doc.meta.id = data.es_id
        return doc.to_dict(True)

    def add(self, clean=False):
        indexed_ids = []
        for type in TYPES:
            objects = DataObject.objects.filter(type=type)
            if not clean:
                objects = objects.exclude(indexed=True)
            for ok, result in streaming_bulk(self.connection, (self.prepare_data(type, obj) for obj in objects)):
                action, result = result.popitem()
                doc_id = "default/_doc/%s" % (result["_id"])
                if not ok:
                    raise IndexError("Failed to {} document {}: {}".format(action, doc_id, result))
                else:
                    o = DataObject.objects.get(es_id=result["_id"])
                    o.indexed = True
                    o.save()
                    indexed_ids.append(doc_id)
        return ("All objects indexed", indexed_ids)

    def delete(self, source, identifier):
        matches = DataObject.find_matches(source, identifier)
        for obj in matches:
            doc_cls = TYPES[obj.type]
            document = doc_cls.get(id=obj.es_id)
            document.delete()
            obj.delete()
