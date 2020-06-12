from rest_framework import serializers

from .models import Creative


class CreativeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Creative
        fields = ('name', 'screenshot', 'screenshot_url')