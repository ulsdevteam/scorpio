from datetime import datetime

from django_cron import CronJobBase, Schedule

from .indexers import Indexer


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
    code = "fetcher.index_all"
    object_type = None


class IndexAllClean(BaseCron):
    code = "fetcher.index_all_clean"
    object_type = None
    clean = True


class IndexAgents(BaseCron):
    code = "fetcher.index_agents"
    object_type = "agent"


class IndexAgentsClean(BaseCron):
    code = "fetcher.index_agents_clean"
    object_type = "agent"
    clean = True


class IndexCollections(BaseCron):
    code = "fetcher.index_collections"
    object_type = "collection"


class IndexCollectionsClean(BaseCron):
    code = "fetcher.index_collections_clean"
    object_type = "collection"
    clean = True


class IndexObjects(BaseCron):
    code = "fetcher.index_objects"
    object_type = "object"


class IndexObjectsClean(BaseCron):
    code = "fetcher.index_objects_clean"
    object_type = "object"
    clean = True


class IndexTerms(BaseCron):
    code = "fetcher.index_terms"
    object_type = "term"


class IndexTermsClean(BaseCron):
    code = "fetcher.index_terms_clean"
    object_type = "term"
    clean = True
