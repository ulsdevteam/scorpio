from rest_framework import serializers

from .models import IndexRun, IndexRunError


class IndexRunErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndexRunError
        fields = ('datetime', 'message')


class IndexRunSerializer(serializers.HyperlinkedModelSerializer):
    errors = IndexRunErrorSerializer(source='indexrunerror_set', many=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = IndexRun
        fields = ('url', 'status', 'object_type', 'object_status', 'error_count',
                  'errors', 'start_time', 'end_time', 'elapsed')

    def get_status(self, obj):
        return obj.STATUS_CHOICES[int(obj.status)][1]


class IndexRunListSerializer(serializers.HyperlinkedModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = IndexRun
        fields = ('url', 'status', 'object_type', 'object_status', 'error_count')

    def get_status(self, obj):
        return obj.STATUS_CHOICES[int(obj.status)][1]
