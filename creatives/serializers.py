from rest_framework import serializers
from .models import Creative


class CreativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Creative
        fields = ['name', 'width', 'height', 'markup']
