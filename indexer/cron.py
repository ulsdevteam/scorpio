from datetime import datetime

from django_cron import CronJobBase, Schedule

from .indexers import Indexer


class BaseCron(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    clean = False

    def do(self):
        start = datetime.now()
        action = "Full" if self.clean else "Incremental"
        print("{} indexing of {} records started at {}".format(action, self.object_type, start))
        indexed = Indexer().add(object_type=self.object_type, clean=self.clean)
        end = datetime.now()
        print("{} records indexed in {}".format(len(indexed), end - start))
        print("{} index of {} records complete at {}\n".format(action, self.object_type, end))


class IndexAll(BaseCron):
    object_type = None


class IndexAllClean(BaseCron):
    object_type = None
    clean = True


class IndexAgents(BaseCron):
    object_type = "agent"


class IndexAgentsClean(BaseCron):
    object_type = "agent"
    clean = True


class IndexCollections(BaseCron):
    object_type = "collection"


class IndexCollectionsClean(BaseCron):
    object_type = "collection"
    clean = True


class IndexObjects(BaseCron):
    object_type = "object"


class IndexObjectsClean(BaseCron):
    object_type = "object"
    clean = True


class IndexTerms(BaseCron):
    object_type = "term"


class IndexTermsClean(BaseCron):
    object_type = "term"
    clean = True
