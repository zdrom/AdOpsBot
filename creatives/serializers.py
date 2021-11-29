from rest_framework import serializers
from .models import Creative


class CreativeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Creative
        fields = ('name', 'width', 'height', 'placement_id', 'markup', 'markup_with_macros')
