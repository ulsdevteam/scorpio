import requests
from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import Index, connections
from electronbonder.client import ElectronBond
from rac_es.documents import (Agent, BaseDescriptionComponent, Collection,
                              Object, Term)
from scorpio import settings

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

    def prepare_deletes(self, id_list):
        for obj_id in id_list:
            try:
                doc = BaseDescriptionComponent.get(id=obj_id)
                yield doc.prepare_streaming_dict(obj_id, self.connection, "delete")
            except Exception as e:
                print(e)

    def fetch_objects(self, object_type, clean):
        """Returns data to be indexed."""
        try:
            url = "objects/{}s/".format(object_type)
            return self.pisces_client.get_paged(url, params={"clean": clean})
        except Exception as e:
            raise Exception("Error fetching objects: {}".format(e))

    def add(self, object_type=None, clean=False, **kwargs):
        """Adds documents to index using ES bulk indexing."""
        object_types = [object_type] if object_type else OBJECT_TYPES
        indexed_ids = []
        for obj_type in object_types:
            current_run = IndexRun.objects.create(
                status=IndexRun.STARTED,
                object_type=obj_type,
                object_status="indexed")
            doc_cls = OBJECT_TYPES[obj_type]
            try:
                indexed_ids += doc_cls.bulk_action(
                    self.connection,
                    self.prepare_updates(obj_type, doc_cls, clean),
                    settings.MAX_OBJECTS)
                current_run.status = IndexRun.FINISHED
                current_run.save()
            except Exception as e:
                print(e)
                IndexRunError.objects.create(
                    message=e,
                    run=current_run)
        update_pisces(indexed_ids, "indexed")
        return indexed_ids

    def delete(self, object_type=None, identifiers=[], **kwargs):
        """Deletes documents from the index using ES bulk indexing."""
        deleted_ids = []
        current_run = IndexRun.objects.create(
            status=IndexRun.STARTED,
            object_type=object_type,
            object_status="deleted")
        try:
            deleted_ids += BaseDescriptionComponent.bulk_action(
                self.connection,
                self.prepare_deletes(identifiers))
            current_run.status = IndexRun.FINISHED
            current_run.save()
        except Exception as e:
            print(e)
            IndexRunError.objects.create(
                message=e,
                run=current_run)
        update_pisces(deleted_ids, "deleted")
        return deleted_ids

    def reset(self, **kwargs):
        try:
            BaseDescriptionComponent._index.delete()
            return "Index deleted.", BaseDescriptionComponent._index._name
        except NotFoundError:
            return "Index does not exist."
