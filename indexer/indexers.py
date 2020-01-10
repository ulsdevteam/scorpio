from elasticsearch_dsl import connections
from elasticsearch.helpers import streaming_bulk
from rac_es.documents import Agent, Collection, Object, Term
from silk.profiling.profiler import silk_profile

from .models import DataObject

from scorpio import settings

OBJECT_TYPES = {
    "agent": Agent,
    "collection": Collection,
    "object": Object,
    "term": Term
}


class ScorpioIndexError(Exception): pass


class Indexer:
    """
    Main indexer class, which adds merged documents to the index or removes
    documents from the index.
    """
    def __init__(self):
        self.connection = connections.create_connection(hosts=settings.ELASTICSEARCH['default']['hosts'], timeout=60)

    def prepare_data(self, object_type, data):
        doc = OBJECT_TYPES[object_type]()
        doc.source = data.data
        doc.meta.id = data.es_id
        return doc.to_dict(True)

    @silk_profile()
    def add(self, clean=False, **kwargs):
        """Adds documents to index. Uses ES bulk indexing."""
        indexed_ids = []
        for obj_type in OBJECT_TYPES:
            objects = DataObject.objects.filter(object_type=obj_type)
            if not clean:
                objects = objects.exclude(indexed=True)
            for ok, result in streaming_bulk(self.connection, (self.prepare_data(obj_type, obj) for obj in objects), refresh=True):
                action, result = result.popitem()
                if not ok:
                    raise ScorpioIndexError("Failed to {} document {}: {}".format(action, result["_id"], result))
                else:
                    o = DataObject.objects.get(es_id=result["_id"])
                    o.indexed = True
                    o.save()
                    indexed_ids.append(result["_id"])
        return ("Indexing complete", indexed_ids)

    @silk_profile()
    def delete(self, source, identifier, **kwargs):
        """
        Deletes data from index. Since this will be a less-regular occurrence,
        this is an atomic (not bulk) operation.
        """
        deleted_ids = []
        matches = DataObject.find_matches(source, identifier)
        for obj in matches:
            doc_cls = OBJECT_TYPES[obj.object_type]
            document = doc_cls.get(id=obj.es_id)
            document.delete(refresh=True)
            deleted_ids.append(obj.es_id)
            obj.delete()
        return ("Deletion complete", deleted_ids)
