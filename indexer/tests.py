import json
import os
from unittest.mock import patch

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

FIXTURE_DIR = "fixtures"


class TestMergerToIndex(TestCase):
    def setUp(self):
        self.client = APIClient()
        connections.create_connection(hosts=settings.ELASTICSEARCH['default']['hosts'], timeout=60)
        try:
            BaseDescriptionComponent._index.delete()
        except NotFoundError:
            pass

    def return_fixture_response(self, dir):
        for f in os.listdir(os.path.join(FIXTURE_DIR, dir)):
            with open(os.path.join(FIXTURE_DIR, dir, f)) as jf:
                data = json.load(jf)
                yield {"data": data, "es_id": data["id"]}

    @patch("indexer.indexers.requests.post")
    @patch("indexer.indexers.Indexer.fetch_objects")
    def index_objects(self, mock_fetch, mock_post):
        """Tests adding objects to index."""
        for cron, fixture_dir in [
                (IndexAgents, "agents"),
                (IndexAgentsClean, "agents"),
                (IndexCollections, "collections"),
                (IndexCollectionsClean, "collections"),
                (IndexObjects, "objects"),
                (IndexObjectsClean, "objects"),
                (IndexTerms, "terms"),
                (IndexTermsClean, "terms"),
                (IndexAll, "terms"),
                (IndexAllClean, "terms")]:
            mock_fetch.return_value = self.return_fixture_response(fixture_dir)
            out = cron().do()
            self.assertIsNot(False, out)

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
