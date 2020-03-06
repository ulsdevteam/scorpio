from elasticsearch.helpers import streaming_bulk
from elasticsearch_dsl import Index, connections
from electronbonder.client import ElectronBond
from rac_es.documents import (Agent, BaseDescriptionComponent, Collection,
                              Object, Term)
from scorpio import settings
from silk.profiling.profiler import silk_profile

OBJECT_TYPES = {
    "agent": Agent,
    "collection": Collection,
    "object": Object,
    "term": Term
}


class ScorpioIndexError(Exception):
    pass


class Indexer:
    """
    Main indexer class, which adds merged documents to the index or removes
    documents from the index.
    """

    def __init__(self):
        self.connection = connections.create_connection(
            hosts=settings.ELASTICSEARCH['default']['hosts'], timeout=60
        )
        if not Index(settings.ELASTICSEARCH['default']['index']).exists():
            BaseDescriptionComponent.init()
        self.pisces_client = ElectronBond(baseurl=settings.PISCES['baseurl'])

    def prepare_data(self, object_type, data):
        doc = OBJECT_TYPES[object_type]()
        doc.source = data["data"]
        doc.meta.id = data["es_id"]
        return doc.to_dict(True)

    @silk_profile()
    def fetch_objects(self, object_type, clean):
        """Returns data to be indexed."""
        url = "objects/{}s/?clean={}".format(object_type, clean)
        return self.pisces_client.get_paged(url)

    @silk_profile()
    def add(self, clean=False, **kwargs):
        """Adds documents to index. Uses ES bulk indexing."""
        indexed_ids = []
        for object_type in OBJECT_TYPES:
            objects = self.fetch_objects(object_type, clean)
            for ok, result in streaming_bulk(self.connection, (self.prepare_data(object_type, obj) for obj in objects), refresh=True):
                action, result = result.popitem()
                if not ok:
                    raise ScorpioIndexError("Failed to {} document {}: {}".format(action, result["_id"], result))
                else:
                    # TODO: Update status in Pisces (obj is not available here, but result is.
                    # Unfortunately that only has the elasticsearch id)
                    print(result)
                    indexed_ids.append(result["_id"])
        return "Indexing complete", indexed_ids

    @silk_profile()
    def delete(self, identifier, **kwargs):
        """
        Deletes data from index. Since this will be a less-regular occurrence,
        this is an atomic (not bulk) operation.
        """
        obj = BaseDescriptionComponent.get(id=identifier)
        obj.delete(refresh=True)
        return "Deletion complete", identifier
