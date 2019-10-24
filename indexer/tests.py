import os
import json

from django.test import TestCase
from elasticsearch_dsl import connections, Search, Index, utils
from rac_es.documents import Agent, BaseDescriptionComponent, Collection, Object, Term
from rest_framework.test import APIRequestFactory

from .helpers import generate_identifier
from .indexers import Indexer, TYPES
from .mergers import BaseMerger
from .models import DataObject
from .views import IndexAddView, IndexDeleteView, MergeView, MERGERS
from scorpio import settings


class TestMergerToIndex(TestCase):
    fixtures = ['initial_state.json']

    def setUp(self):
        self.factory = APIRequestFactory()
        # TODO: create and connect to test index
        connections.create_connection(hosts=settings.ELASTICSEARCH['default']['hosts'], timeout=60)
        BaseDescriptionComponent.init()
        self.object_len = len(DataObject.objects.all())

    def merge_objects(self):
        # TODO: better set of objects to be merged
        for dir in os.listdir(os.path.join(settings.BASE_DIR, 'fixtures')):
            if os.path.isdir(os.path.join(settings.BASE_DIR, 'fixtures', dir)):
                for f in os.listdir(os.path.join(settings.BASE_DIR, 'fixtures', dir)):
                    with open(os.path.join(settings.BASE_DIR, 'fixtures', dir, f), 'r') as jf:
                        instance = json.load(jf)
                        merger = MERGERS[instance.get('type')]()
                        merged = merger.merge(instance)
        self.assertEqual(self.object_len, len(DataObject.objects.all()))
        # check field values
        # check valid against jsonschema - or should this be baked into merger?

    def index_objects(self):
        # TODO: pass connection to test ES index
        indexed = Indexer().add()
        self.assertNotEqual(indexed, False)
        self.assertEqual(self.object_len, len(indexed[1]))
        # TODO: test number of objects in index

    def delete_objects(self):
        # TODO: pass connection to test ES index
        for obj in DataObject.objects.all():
            for id_obj in obj.data['external_identifiers']:
                deleted = Indexer().delete(id_obj['source'], id_obj['identifier'])
                self.assertNotEqual(deleted, False)
        # TODO: test number of objects in index

    # TODO: test views

    def test_process(self):
        self.merge_objects()
        self.index_objects()
        self.delete_objects()
