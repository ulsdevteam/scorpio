import json
import os
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import connections
from rac_es.documents import BaseDescriptionComponent
from rest_framework.test import APIClient, APIRequestFactory
from scorpio import settings

from .cron import (IndexAgents, IndexAgentsClean, IndexAll, IndexAllClean,
                   IndexCollections, IndexCollectionsClean, IndexObjects,
                   IndexObjectsClean, IndexTerms, IndexTermsClean)
from .models import IndexRun, IndexRunError
from .views import IndexRunViewSet

FIXTURE_DIR = "fixtures"


class TestMergerToIndex(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()
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
        fetches = 0
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
            if cron in [IndexAll, IndexAllClean]:
                fetches += 4
            else:
                fetches += 1
            self.assertTrue(out)
            self.assertEqual(len(IndexRun.objects.all()), fetches)
            self.assertEqual(len(IndexRunError.objects.all()), 0)
            for obj in IndexRun.objects.all():
                self.assertEqual(int(obj.status), IndexRun.FINISHED)

    @patch("indexer.indexers.requests.post")
    def delete_objects(self, mock_post):
        """Tests object deletion from index."""
        to_delete = []
        for obj in BaseDescriptionComponent.search().scan():
            to_delete.append(obj.meta.id)
        request = self.client.post(reverse("index-delete"), json.dumps({"identifiers": to_delete}), content_type="application/json")
        self.assertEqual(request.status_code, 200, "Index delete error: {}".format(request.data))
        self.assertEqual(mock_post.call_count, 1)
        self.assertTrue(mock_post.called_with({}))
        self.assertEqual(0, BaseDescriptionComponent.search().count())

    def test_action_views(self):
        for action in ["agents", "collections", "objects", "terms"]:
            view = IndexRunViewSet.as_view({"get": action})
            request = self.factory.get("fetchrun-list")
            response = view(request)
            self.assertEqual(
                response.status_code, 200,
                "View error: {}".format(response.data))

    def test_process(self):
        self.index_objects()
        self.delete_objects()
