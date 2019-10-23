from elasticsearch_dsl import connections
from elasticsearch.helpers import streaming_bulk
from rac_es.documents import Agent, Collection, Object, Term

from .models import DataObject

from scorpio import config

TYPES = {
    "agent": Agent,
    "collection": Collection,
    "object": Object,
    "term": Term
}


class Indexer:

    def __init__(self):
        self.connection = connections.create_connection(hosts=settings.ELASTICSEARCH['default']['hosts'], timeout=60)

    def prepare_data(self, data):
        doc = TYPES[type](data)
        return doc.to_dict(True)

    def add(self, clean=False):
        for type in TYPES:
            objects = DataObject.objects.filter(type=type)
            if not clean:
                objects = objects.exclude(indexed=True)
            for ok, result in streaming_bulk(self.connection, (prepare_data(obj) for obj in objects)):
                action, result = result.popitem()
                doc_id = "/%s/doc/%s" % (index, result["_id"])
                if not ok:
                    print("Failed to %s document %s: %r" % (action, doc_id, result))
                else:
                    o = DataObject.objects.get(es_id=result["_id"])
                    o.indexed = True
                    o.save()

    def delete(self):
        json = data_to_json(data)
        doc_cls = get_doc_cls(data)
        document = doc_cls.get(id=json['_id'])
        document.delete()
