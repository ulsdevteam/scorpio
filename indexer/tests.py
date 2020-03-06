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
        with indexer_vcr.use_cassette("index-add.json"):
            request = self.client.post(reverse("index-add"))
            self.assertEqual(request.status_code, 200, "Index add error: {}".format(request.data))
            # TODO: test counts
            # TODO: test clean

    def delete_objects(self):
        for hit in BaseDescriptionComponent.search().execute():
            request = self.client.post(reverse("index-delete"), {"identifier": hit.meta.id})
            self.assertEqual(request.status_code, 200, "Index delete error: {}".format(request.data))
        self.assertEqual(0, BaseDescriptionComponent.search().count())

    def test_process(self):
        self.index_objects()
        self.delete_objects()
