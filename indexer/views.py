from rest_framework.views import APIView

from .indexers import Indexer


class IndexAddView(APIView):
    """Adds a data object to index."""

    def post(self, request, format=None):
        data = request.data.get('data')
        try:
            resp = Indexer().add_single(data)
            return Response({"detail": resp}, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=500)


class IndexDeleteView(APIView):
    """Deletes a data object from index."""

    def post(self, request, format=None):
        data = request.data.get('data')
        try:
            resp = Indexer().delete_single(data)
            return Response({"detail": resp}, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=500)
