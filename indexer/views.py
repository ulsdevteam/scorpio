from asterism.views import prepare_response
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .indexers import Indexer
from .models import DataObject
from .mergers import AgentMerger, CollectionMerger, ObjectMerger, TermMerger
from .serializers import DataObjectSerializer

MERGERS = {
    "agent": AgentMerger,
    "collection": CollectionMerger,
    "object": ObjectMerger,
    "term": TermMerger
}


class IndexView(APIView):
    """Add data to or delete data from an index"""
    def post(self, request, format=None):
        clean = True if request.GET.get('clean') else False
        source = request.data.get('source')
        identifier = request.data.get('identifier')
        try:
            resp = getattr(Indexer(), self.method)(clean=clean, source=source, identifier=identifier)
            return Response(prepare_response(resp), status=200)
        except Exception as e:
            return Response(prepare_response(e), status=500)


class IndexAddView(IndexView):
    """Adds a data object to index."""
    method = 'add'


class IndexDeleteView(IndexView):
    """Deletes a data object from index."""
    method = 'delete'


class MergeView(APIView):
    """Merges transformed data objects."""
    def post(self, request, format=None):
        if not request.data:
            return Response(prepare_response("No data submitted to merge",), status=500)
        try:
            merger = MERGERS[request.data['type']]()
            resp = merger.merge(request.data)
            return Response(prepare_response(resp), status=200)
        except Exception as e:
            return Response(prepare_response(e), status=500)


class DataObjectViewSet(ModelViewSet):
    model = DataObject
    queryset = DataObject.objects.all()
    serializer_class = DataObjectSerializer
