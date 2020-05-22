from unittest.mock import patch

import vcr
from django.test import TestCase
from django.urls import reverse
from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import connections
from rac_es.documents import BaseDescriptionComponent, DescriptionComponent
from rest_framework.test import APIClient
from scorpio import settings

from .cron import (IndexAgents, IndexAgentsClean, IndexAll, IndexAllClean,
                   IndexCollections, IndexCollectionsClean, IndexObjects,
                   IndexObjectsClean, IndexTerms, IndexTermsClean)

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
        for cron, cassette, count in [
                (IndexAgents, "index-add-agent-incremental.json", 83),
                (IndexAgentsClean, "index-add-agent-clean.json", 83),
                (IndexCollections, "index-add-collection-incremental.json", 99),
                (IndexCollectionsClean, "index-add-collection-clean.json", 99),
                (IndexObjects, "index-add-object-incremental.json", 58),
                (IndexObjectsClean, "index-add-object-clean.json", 58),
                (IndexTerms, "index-add-term-incremental.json", 45),
                (IndexTermsClean, "index-add-term-clean.json", 45),
                (IndexAll, "index-add-None-incremental.json", 0),
                (IndexAllClean, "index-add-None-clean.json", 285)]:
            with indexer_vcr.use_cassette(cassette):
                out = cron().do()
                self.assertIsNot(False, out)
                self.assertEqual(DescriptionComponent.search().count(), count)

    @patch("indexer.indexers.requests.post")
    def delete_objects(self, mock_post):
        """Tests object deletion from index."""
        expected_len = DescriptionComponent.search().count()
        for obj in DescriptionComponent.search().scan():
            request = self.client.post(reverse("index-delete"), {"identifier": obj.meta.id})
            self.assertEqual(request.status_code, 200, "Index delete error: {}".format(request.data))
        self.assertEqual(mock_post.call_count, expected_len)
        self.assertEqual(0, BaseDescriptionComponent.search().count())

    def test_process(self):
        self.index_objects()
        self.delete_objects()
