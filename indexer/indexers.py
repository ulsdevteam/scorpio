import json
import shortuuid

from elasticsearch_dsl import connections, Search
from rac_es.documents import Agent, Collection, Object, Term

from scorpio import config

TYPES = {
    "agent": Agent,
    "collection": Collection,
    "object": Object,
    "term": Term
}


class Indexer:

    def __init__(self):
        connections.create_connection(hosts=settings.ELASTICSEARCH['default']['hosts'], timeout=60)

    def data_to_json(self, data):
        if isinstance(data, str):
            data = json.loads(data)
        return data

    def get_doc_cls(self, data):
        return TYPES[json['type']]

    def add(self, data):
        json = data_to_json(data)
        doc_cls = get_doc_cls(data)
        document = doc_cls(**json)
        document.meta.id = json['id']
        document.save()

    def delete(self, data):
        json = data_to_json(data)
        doc_cls = get_doc_cls(data)
        document = doc_cls.get(id=json['_id'])
        document.delete()
