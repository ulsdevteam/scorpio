from datetime import datetime

from django_cron import CronJobBase, Schedule

from .indexers import Indexer
from .models import IndexRun


class BaseCron(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    clean = False

    def do(self):
        result = False
        start = datetime.now()
        action = "Full" if self.clean else "Incremental"
        object_type = self.object_type if self.object_type else "all"
        indexed = []
        print("{} indexing of {} records started at {}".format(action, object_type, start))
        try:
            indexed = Indexer().add(object_type=self.object_type, clean=self.clean)
        except Exception as e:
            print(e)
        end = datetime.now()
        print("{} records indexed in {}".format(len(indexed), end - start))
        print("{} index of {} records complete at {}\n".format(action, object_type, end))
        result = True
        return result


class IndexAll(BaseCron):
    code = "indexer.index_all"
    object_type = None


class IndexAllClean(BaseCron):
    code = "indexer.index_all_clean"
    object_type = None
    clean = True


class IndexAgents(BaseCron):
    code = "indexer.index_agents"
    object_type = "agent"


class IndexAgentsClean(BaseCron):
    code = "indexer.index_agents_clean"
    object_type = "agent"
    clean = True


class IndexCollections(BaseCron):
    code = "indexer.index_collections"
    object_type = "collection"


class IndexCollectionsClean(BaseCron):
    code = "indexer.index_collections_clean"
    object_type = "collection"
    clean = True


class IndexObjects(BaseCron):
    code = "indexer.index_objects"
    object_type = "object"


class IndexObjectsClean(BaseCron):
    code = "indexer.index_objects_clean"
    object_type = "object"
    clean = True


class IndexTerms(BaseCron):
    code = "indexer.index_terms"
    object_type = "term"


class IndexTermsClean(BaseCron):
    code = "indexer.index_terms_clean"
    object_type = "term"
    clean = True


class CleanUpCompleted(CronJobBase):
    """Deletes all IndexRuns without errors."""
    code = "indexer.cleanup_completed"
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)

    def do(self):
        try:
            return IndexRun.objects.filter(indexrunerror__isnull=True).delete()
        except Exception as e:
            print("Error cleaning up completed IndexRun objects: {}".format(e))
            return False
