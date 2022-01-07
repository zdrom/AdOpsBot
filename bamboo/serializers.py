from rest_framework import serializers
from .models import PTO, Holidays


class PTOSerializer(serializers.ModelSerializer):
    class Meta:
        model = PTO
        fields = ['request_id', 'start', 'end', 'team_member', 'coverage']


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holidays
        fields = ['name', 'date']