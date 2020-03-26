import vcr
from django.test import TestCase
from django.urls import reverse
from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import connections
from rac_es.documents import BaseDescriptionComponent
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
        for clean in [False, True]:
            for object_type in ["agent", "collection", "object", "term", None]:
                with indexer_vcr.use_cassette(
                        "index-add-{}-{}.json".format(
                            object_type, "clean" if clean else "incremental")):
                    data = {"object_type": object_type, "clean": clean} if object_type else {"clean": clean}
                    request = self.client.post(reverse("index-add"), data=data)
                    self.assertEqual(
                        request.status_code, 200,
                        "Index add error: {}".format(request.data))

    def delete_objects(self):
        """Tests object deletion from index."""
        with indexer_vcr.use_cassette("index-delete"):
            for hit in BaseDescriptionComponent.search().scan():
                request = self.client.post(reverse("index-delete"), {"identifier": hit.meta.id})
                self.assertEqual(request.status_code, 200, "Index delete error: {}".format(request.data))
            self.assertEqual(0, BaseDescriptionComponent.search().count())

    def test_process(self):
        self.index_objects()
        self.delete_objects()
