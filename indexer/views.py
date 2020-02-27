from asterism.views import BaseServiceView
from rest_framework.viewsets import ModelViewSet

from .indexers import Indexer
from .mergers import AgentMerger, CollectionMerger, ObjectMerger, TermMerger
from .models import DataObject
from .serializers import DataObjectListSerializer, DataObjectSerializer

MERGERS = {
    "agent": AgentMerger,
    "collection": CollectionMerger,
    "object": ObjectMerger,
    "term": TermMerger
}


class IndexView(BaseServiceView):
    """Add data to or delete data from an index"""

    def get_service_response(self, request):
        clean = True if request.GET.get('clean') else False
        source = request.data.get('source')
        identifier = request.data.get('identifier')
        return getattr(Indexer(), self.method)(clean=clean, source=source, identifier=identifier)


class IndexAddView(IndexView):
    """Adds a data object to index."""
    method = 'add'


class IndexDeleteView(IndexView):
    """Deletes a data object from index."""
    method = 'delete'


class MergeView(BaseServiceView):
    """Merges transformed data objects."""

    def get_service_response(self, request):
        if not request.data:
            raise Exception("No data submitted to merge")
        merger = MERGERS[request.data['type']]()
        return merger.merge(request.data)


class DataObjectViewSet(ModelViewSet):
    model = DataObject
    queryset = DataObject.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return DataObjectListSerializer
        return DataObjectSerializer
