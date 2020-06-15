from asterism.views import BaseServiceView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .indexers import Indexer
from .models import IndexRun
from .serializers import IndexRunListSerializer, IndexRunSerializer


class IndexRunViewSet(ModelViewSet):
    """
    retrieve:
        Return data about a IndexRun object, identified by a primary key.

    list:
        Return paginated data about all IndexRun objects.
    """
    model = IndexRun
    queryset = IndexRun.objects.all().order_by("-start_time")

    def get_serializer_class(self):
        if self.action not in ["create", "retrieve", "update", "partial_update", "destroy"]:
            return IndexRunListSerializer
        return IndexRunSerializer

    def get_action_response(self, request, object_type):
        queryset = IndexRun.objects.filter(object_type=object_type).order_by("-start_time")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def agents(self, request):
        return self.get_action_response(request, "agent")

    @action(detail=False)
    def collections(self, request):
        return self.get_action_response(request, "collection")

    @action(detail=False)
    def objects(self, request):
        return self.get_action_response(request, "object")

    @action(detail=False)
    def terms(self, request):
        return self.get_action_response(request, "term")


class IndexView(BaseServiceView):
    """Add data to or delete data from an index."""

    def get_service_response(self, request):
        clean = request.data.get("clean")
        identifier = request.data.get("identifier")
        object_type = request.data.get("object_type")
        indexed = getattr(
            Indexer(), self.method)(
                clean=clean, object_type=object_type, identifier=identifier)
        return "{} indexed".format(object_type), indexed


class IndexDeleteView(IndexView):
    """Deletes a data object from index."""
    method = "delete"


class IndexResetView(IndexView):
    """Deletes the entire index."""
    method = "reset"
