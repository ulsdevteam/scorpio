import requests
from elasticsearch.exceptions import NotFoundError
from elasticsearch.helpers import streaming_bulk
from elasticsearch_dsl import Index, connections
from electronbonder.client import ElectronBond
from rac_es.documents import (Agent, BaseDescriptionComponent, Collection,
                              DescriptionComponent, Object, Term)
from scorpio import settings
from silk.profiling.profiler import silk_profile

from .models import IndexRun, IndexRunError

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

    def prepare_updates(self, obj_type, doc_cls, clean):
        for obj in self.fetch_objects(obj_type, clean):
            doc = doc_cls(**obj["data"])
            try:
                yield doc.prepare_streaming_dict(obj["es_id"], self.connection)
            except Exception as e:
                raise Exception("Error preparing streaming dict: {}".format(e))

    def prepare_deletes(self, obj):
        for reference in list(obj.get_references()) + [obj]:
            doc = reference.to_dict(True)
            doc["_op_type"] = "delete"
            yield doc

    @silk_profile()
    def fetch_objects(self, object_type, clean):
        """Returns data to be indexed."""
        try:
            url = "objects/{}s/".format(object_type)
            return self.pisces_client.get_paged(url, params={"clean": clean})
        except Exception as e:
            raise Exception("Error fetching objects: {}".format(e))

    def bulk_index_action(self, actions, completed_action):
        indexed_ids = []
        indexed_count = 0
        try:
            for ok, result in streaming_bulk(self.connection, actions, refresh=True):
                action, result = result.popitem()
                if not ok:
                    update_pisces(indexed_ids, completed_action)
                    raise ScorpioIndexError("Failed to {} document {}: {}".format(action, result["_id"], result))
                else:
                    indexed_ids.append(result["_id"])
                    indexed_count += 1
                if indexed_count == settings.MAX_OBJECTS:
                    break
        except Exception as e:
            update_pisces(indexed_ids, completed_action)
            print(e)
        update_pisces(indexed_ids, completed_action)
        return indexed_ids

    @silk_profile()
    def add(self, object_type=None, clean=False, **kwargs):
        """Adds documents to index. Uses ES bulk indexing."""
        object_types = [object_type] if object_type else OBJECT_TYPES
        indexed_ids = []
        for obj_type in object_types:
            current_run = IndexRun.objects.create(
                status=IndexRun.STARTED,
                object_type=obj_type,
                object_status="indexed")
            doc_cls = OBJECT_TYPES[obj_type]
            try:
                indexed_ids += doc_cls.bulk_save(
                    self.connection,
                    self.prepare_updates(obj_type, doc_cls, clean),
                    obj_type,
                    settings.MAX_OBJECTS)
            except ScorpioIndexError as e:
                IndexRunError.objects.create(
                    message=e,
                    run=current_run)
        update_pisces(indexed_ids, "indexed")
        current_run.status = IndexRun.FINISHED
        current_run.save()
        return indexed_ids

    @silk_profile()
    def delete(self, identifier, **kwargs):
        """
        Deletes a DescriptionComponent from the index, along with all its
        associated references. Uses ES bulk indexing.
        """
        obj = DescriptionComponent.get(id=identifier)
        return self.bulk_index_action(self.prepare_deletes(obj), "deleted")

    def reset(self, **kwargs):
        try:
            BaseDescriptionComponent._index.delete()
            return "Index deleted.", BaseDescriptionComponent._index._name
        except NotFoundError:
            return "Index does not exist."
