import json
import os

from django.test import TestCase
from django.urls import reverse
from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import connections
from rac_es.documents import BaseDescriptionComponent
from rest_framework.test import APIClient
from scorpio import settings

from .mergers import AgentMerger, CollectionMerger, ObjectMerger, TermMerger
from .models import DataObject


class TestMergerToIndex(TestCase):
    fixtures = ['initial_state.json']

    def setUp(self):
        self.client = APIClient()
        connections.create_connection(hosts=settings.ELASTICSEARCH['default']['hosts'], timeout=60)
        try:
            BaseDescriptionComponent._index.delete()
        except NotFoundError:
            pass
        BaseDescriptionComponent.init()
        self.object_len = len(DataObject.objects.all())

    def check_merged_values(self, transformed_data, merged_data):
        MERGERS = {
            "agent": AgentMerger,
            "collection": CollectionMerger,
            "object": ObjectMerger,
            "term": TermMerger
        }
        merger = MERGERS[merged_data['type']]
        for identifier in transformed_data['external_identifiers']:
            source = identifier['source']
            if hasattr(merger, 'single_source_fields'):
                for field in merger.single_source_fields[source]:
                    self.assertEqual(transformed_data.get(field), merged_data.get(field))
            if hasattr(merger, 'multi_source_fields'):
                for field in merger.multi_source_fields:
                    transformed_objs = [obj for obj in transformed_data.get(field) if obj['source'] == source]
                    merged_objs = [obj for obj in merged_data.get(field) if obj['source'] == source]
                    self.assertEqual(transformed_objs, merged_objs)

    def merge_objects(self):
        for dir in os.listdir(os.path.join(settings.BASE_DIR, 'fixtures', 'queued')):
            if os.path.isdir(os.path.join(settings.BASE_DIR, 'fixtures', 'queued', dir)):
                for f in os.listdir(os.path.join(settings.BASE_DIR, 'fixtures', 'queued', dir)):
                    with open(os.path.join(settings.BASE_DIR, 'fixtures', 'queued', dir, f), 'r') as jf:
                        instance = json.load(jf)
                        request = self.client.post(reverse("merge"), instance, format='json')
                        print(request.data)
                        self.assertEqual(request.status_code, 200)
                        merged = DataObject.objects.get(es_id=request.data['objects'][0])
                        self.check_merged_values(instance, merged.data)
        self.assertEqual(self.object_len, len(DataObject.objects.all()))

    def index_objects(self):
        BaseDescriptionComponent._index.delete()  # Delete index to ensure view recreates it properly
        request = self.client.post(reverse("index-add"))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(self.object_len, request.data['count'])
        self.assertEqual(self.object_len, BaseDescriptionComponent.search().count())

    def delete_objects(self):
        for obj in DataObject.objects.all():
            for id_obj in obj.data['external_identifiers']:
                request = self.client.post(reverse("index-delete"), {"source": id_obj['source'], "identifier": id_obj['identifier']})
                self.assertEqual(request.status_code, 200)
        self.assertEqual(0, BaseDescriptionComponent.search().count())

    def test_process(self):
        self.merge_objects()
        self.index_objects()
        self.delete_objects()
