import requests
from elasticsearch.exceptions import NotFoundError
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


def update_pisces(identifiers, action):
    try:
        resp = requests.post("/".join([
            settings.PISCES["baseurl"].rstrip("/"),
            settings.PISCES["post_index_path"].lstrip("/")]),
            json={"identifiers": identifiers, "action": action})
        resp.raise_for_status()
    except requests.HTTPError as e:
        print("Error sending request to Pisces: {}".format(e.response.json()["detail"]))


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

    def prepare_data(self, obj_type, clean):
        for obj in self.fetch_objects(obj_type, clean):
            doc = OBJECT_TYPES[obj_type](**obj["data"])
            yield doc.prepare_streaming_dict(obj["es_id"])

    @silk_profile()
    def fetch_objects(self, object_type, clean):
        """Returns data to be indexed."""
        url = "objects/{}s/".format(object_type)
        return self.pisces_client.get_paged_reverse(url, params={"clean": clean})

    @silk_profile()
    def add(self, object_type=None, clean=False, **kwargs):
        """Adds documents to index. Uses ES bulk indexing."""
        indexed_ids = []
        object_types = [object_type] if object_type else OBJECT_TYPES
        for obj_type in object_types:
            for ok, result in streaming_bulk(self.connection, self.prepare_data(obj_type, clean), refresh=True):
                action, result = result.popitem()
                if not ok:
                    update_pisces(indexed_ids, "indexed")
                    raise ScorpioIndexError("Failed to {} document {}: {}".format(action, result["_id"], result))
                else:
                    indexed_ids.append(result["_id"])
        if indexed_ids:
            update_pisces(indexed_ids, "indexed")
        return indexed_ids

    @silk_profile()
    def delete(self, identifier, **kwargs):
        """
        Deletes data from index. Since this will be a less-regular occurrence,
        this is an atomic (not bulk) operation.
        """
        obj = BaseDescriptionComponent.get(id=identifier)
        obj.delete(refresh=True)
        update_pisces([identifier], "deleted")
        return "Deletion complete", identifier

    def reset(self, **kwargs):
        try:
            BaseDescriptionComponent._index.delete()
            return "Index deleted.", BaseDescriptionComponent._index._name
        except NotFoundError:
            return "Index does not exist."
