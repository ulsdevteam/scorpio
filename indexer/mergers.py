from elasticsearch_dsl import connections, Search
from rac_es.documents import Agent, Collection, Object, Term


class BaseMerger:
    """
    Base merger class. Should be subclassed by object-specific mergers which
    provide `single_source_fields` and `multi_source_fields` properties.

    `single_source_fields` is a dict which specifies a list of fields for each
    source:
        {'archivesspace': ['title', 'children' ...], 'wikidata': 'image_url'}

    `multi_source_fields` is a list of fields matched by multiple sources:
        ['notes', 'dates', 'external_identifiers']
     """

    def __init__(self):
        if not self.document:
            raise Exception("Missing required `document` property on self")
        if not (self.single_source_fields and self.multi_source_fields):
            raise Exception("Both `single_source_fields` and `multi_source_fields` properties are required on self.")
        if not isinstance(self.single_source_fields, dict):
            raise Exception("`self.single_source_fields` property should be a dictionary")
        if not isinstance(self.multi_source_fields, list):
            raise Exception("`self.multi_source_fields` property should be a list")
        self.client = connections.create_connection(hosts=settings.ELASTICSEARCH['default']['hosts'], timeout=60)
        self.search = self.document.search(using=self.client)

    def find_matches(self, source_id):
        queryset = self.search.query()
        queryset = queryset.filter('match_phrase', **{'source_id': source_id})
        return queryset.execute().hits

    def apply_single_source_merges(self, transformed, match, source):
        """Replaces fields that have only one possible source and match the
           incoming object's source."""
        for field in self.single_source_fields[source]:
            match[field] = transformed[field]
        return match

    def apply_multi_source_merges(self, transformed, match, source):
        """Merge multi-source fields by removing matching nested objects and then
           adding new nested objects."""
        for field in self.multi_source_fields:
            for field_obj in match[field]:
                if field_obj.source == source:
                    match[field].remove(field_obj)
            match[field].append(transformed[field])
        return match

    def merge(self, object):
        """Main merge function. Merges transformed object into matched objects
           if they exist, or simply passes on the transformed object if no
           matches are found."""
        for identifier in object.external_identifiers:
            matches = self.find_matches("{}_{}".format(identifier.source, identifier.identifier))
            if len(matches):
                for match in matches:
                    single_merge = self.apply_single_source_merges(object, match, identifier.source)
                    multi_merge = self.apply_multi_source_merges(object, single_merge, identifier.source)
                    #self.persist(multi)
            else:
                pass
                # create Elasticsearch identifier
                # self.persist(object)


class AgentMerger(BaseMerger):
    """Merges transformed Agents data"""
    document = Agent
    single_source_fields = {"archivesspace": [], "cartographer": []}
    multi_source_fields = []


class CollectionMerger(BaseMerger):
    document = Collection
    single_source_fields = {"archivesspace": [], "cartographer": []}
    multi_source_fields = []


class ObjectMerger(BaseMerger):
    document = Object
    single_source_fields = {"archivesspace": [], "cartographer": []}
    multi_source_fields = []


class TermMerger(BaseMerger):
    document = Term
    single_source_fields = {"archivesspace": [], "cartographer": []}
    multi_source_fields = []
