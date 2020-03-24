import vcr
from django.test import TestCase
from django.urls import reverse
from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import connections
from rac_es.documents import (Agent, BaseDescriptionComponent, Collection,
                              Object, Term)
from rest_framework.test import APIClient
from scorpio import settings

indexer_vcr = vcr.VCR(
    serializer="json",
    cassette_library_dir="fixtures/cassettes",
    record_mode="once",
    match_on=["path", "method", "query"],
    filter_query_parameters=["username", "password"],
    filter_headers=["Authorization", "X-ArchivesSpace-Session"],
    ignore_hosts=["elasticsearch"]
)


class TestMergerToIndex(TestCase):
    def setUp(self):
        self.client = APIClient()
        connections.create_connection(hosts=settings.ELASTICSEARCH['default']['hosts'], timeout=60)
        try:
            BaseDescriptionComponent._index.delete()
        except NotFoundError:
            pass

    def index_objects(self):
        """Tests adding objects to index."""
        for clean in [True, False]:
            for object_type, document in [
                    ("agent", Agent), ("collection", Collection),
                    ("object", Object), ("term", Term), ("", None)]:
                with indexer_vcr.use_cassette(
                        "index-add-{}-{}.json".format(
                            object_type, "clean" if clean else "incremental")):
                    request = self.client.post(
                        "{}?object_type={}&clean={}".format(
                            reverse("index-add"), object_type, clean))
                    self.assertEqual(
                        request.status_code, 200,
                        "Index add error: {}".format(request.data))

    def delete_objects(self):
        """Tests object deletion from index."""
        with indexer_vcr.use_cassette("index-delete"):
            for hit in BaseDescriptionComponent.search().execute():
                request = self.client.post(reverse("index-delete"), {"identifier": hit.meta.id})
                self.assertEqual(request.status_code, 200, "Index delete error: {}".format(request.data))
            self.assertEqual(0, BaseDescriptionComponent.search().count())

    def test_process(self):
        self.index_objects()
        self.delete_objects()
