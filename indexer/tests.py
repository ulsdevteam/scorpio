import os
import json

from django.test import TestCase
from elasticsearch_dsl import connections, Search, Index, utils
from rac_es.documents import Agent, BaseDescriptionComponent, Collection, Object, Term
from rest_framework.test import APIRequestFactory

from .helpers import generate_identifier
from .mergers import BaseMerger
from .models import DataObject
from .views import IndexAddView, IndexDeleteView, MergeView
from scorpio import settings


class TestMergerToIndex(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        connections.create_connection(hosts=settings.ELASTICSEARCH['default']['hosts'], timeout=60)
        # BaseDescriptionComponent.init()
        for dir in os.listdir(os.path.join(settings.BASE_DIR, 'fixtures')):
            if os.path.isdir(os.path.join(settings.BASE_DIR, 'fixtures', dir)):
                for f in os.listdir(os.path.join(settings.BASE_DIR, 'fixtures', dir)):
                    with open(os.path.join(settings.BASE_DIR, 'fixtures', dir, f), 'r') as jf:
                        instance = json.load(jf)
                        DataObject.objects.create(es_id=generate_identifier(),
                                                        type=dir.rstrip('s'),
                                                        data=instance)

    def merge_objects(self): pass
        # merge objects using routine
        # check field values
        # check valid against jsonschema
        # check merge view response

    def index_objects(self): pass
        # index merged objects of each type
        # check number of indexed objects

    def delete_objects(self): pass
        # delete objects
        # check number of objects in index

    def test_process(self):
        self.merge_objects()
        self.index_objects()
        self.delete_objects()
