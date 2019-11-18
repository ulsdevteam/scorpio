from rac_es.documents import Agent, Collection, Object, Term
from silk.profiling.profiler import silk_profile

from .helpers import generate_identifier
from .models import DataObject


class MergeError(Exception):
    pass


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
        if not self.type:
            raise Exception("Missing required `type` property on self")
        if not (hasattr(self, 'single_source_fields') and hasattr(self, 'multi_source_fields')):
            raise Exception(
                "Both `single_source_fields` and `multi_source_fields` properties are required on self.")
        if not isinstance(self.single_source_fields, dict):
            raise Exception(
                "`self.single_source_fields` property should be a dictionary")
        if not isinstance(self.multi_source_fields, list):
            raise Exception(
                "`self.multi_source_fields` property should be a list")

    @silk_profile()
    def apply_single_source_merges(self, transformed, match, source):
        """Replaces fields that have only one possible source and match the
           incoming object's source."""
        for field in self.single_source_fields[source]:
            match[field] = transformed.get(field)
        return match

    @silk_profile()
    def apply_multi_source_merges(self, transformed, match, source):
        """Merge multi-source fields by removing matching nested objects and then
           adding new nested objects. Match lists are traversed in reverse order
           so that all list items are acted on."""
        for field in self.multi_source_fields:
            if match.get(field):
                for field_obj in reversed(match[field]):
                    if field_obj.get('source') == source:
                        match[field].remove(field_obj)
                for f in transformed[field]:
                    match[field].append(f)
        return match

    @silk_profile()
    def apply_tree_merges(self, transformed, match, source):
        if match.get('type') in ['collection', 'object']:
            pass
            # if sources match:
                # replace match ancestors with transformed ancestors
                # if match children attr exists:
                    # replace match children with transformed children if exists
            # else:
                # children
                    # if transformed source = cartographer:
                        # replace match children with transformed children
                    # if transformed source = archivesspace
                        # replace if match source = archivespace this is already handled above?
                # ancestors
                    # if transformed source = cartographer
                        # remove ancestors with source=cartographer from match
                        # prepend transformed ancestors to match ancestors
                    # if transformed source = archivesspace
                        # remove ancestors with source=cartographer from match
                        # append transformed ancestors to match ancestors
        return match

    @silk_profile()
    def merge_external_identifiers(self, transformed, match):
        for ex_id in transformed.get('external_identifiers'):
            if ex_id not in match.get(external_identifiers):
                match.get('external_identifiers', []).append(ex_id)
        return match

    @silk_profile()
    def merge(self, object):
        """Main merge function. Merges transformed object into matched objects
           if they exist and then persists the merged object, or simply persists
           the transformed object if no matches are found."""
        try:
            merged_ids = []
            for identifier in object['external_identifiers']:
                matches = DataObject.find_matches(identifier['source'],
                                                  identifier['identifier'],
                                                  initial_queryset=DataObject.objects.filter(type=self.type))
                if len(matches):
                    for match in matches:
                        single_merge = self.apply_single_source_merges(
                            object, match.data, identifier['source'])
                        multi_merge = self.apply_multi_source_merges(
                            object, single_merge, identifier['source'])
                        tree_merge = self.apply_tree_merges(
                            object, multi_merge, identifier['source'])
                        external_id_merge = self.merge_external_identifiers(
                            object, tree_merge)
                        match.data = external_id_merge
                        match.indexed = False
                        match.save()
                        merged_ids.append(match.es_id)
                else:
                    es_id = generate_identifier()
                    doc = DataObject.objects.create(es_id=es_id,
                                                    data=object,
                                                    type=self.type,
                                                    indexed=False)
                    merged_ids.append(es_id)
            return ("Object merged", merged_ids)
        except Exception as e:
            raise MergeError("Error merging: {}".format(e))


class AgentMerger(BaseMerger):
    """Merges transformed Agent data."""
    type = 'agent'
    single_source_fields = {"archivesspace": [
        "title", "agent_type", "collections", "objects"], "wikidata": ["description"]}
    multi_source_fields = ["dates", "notes"]


class CollectionMerger(BaseMerger):
    """Merges transformed Agent data."""
    type = 'collection'
    single_source_fields = {"archivesspace": [
        "title", "level", "dates", "creators", "languages", "extents", "notes", "agents", "terms", "rights_statements"]}
    multi_source_fields = []


class ObjectMerger(BaseMerger):
    """Merges transformed Agent data."""
    type = 'object'
    single_source_fields = {"archivesspace": [
        "title", "dates", "languages", "extents", "notes", "agents", "terms", "rights_statements"]}
    multi_source_fields = []


class TermMerger(BaseMerger):
    """Merges transformed Agent data."""
    type = 'term'
    single_source_fields = {"archivesspace": ["title", "term_type"]}
    multi_source_fields = []
