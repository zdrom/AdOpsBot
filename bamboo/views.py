from django.http import HttpResponse
from rest_framework import viewsets, permissions

from bamboo.models import PTO, Holidays
from bamboo.serializers import PTOSerializer, HolidaySerializer
from django.core.management import call_command

from bamboo.models import PTO, Team


class PTOViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = PTO.objects.all()
    serializer_class = PTOSerializer
    permission_classes = [permissions.IsAuthenticated]


class HolidayViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Holidays.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [permissions.IsAuthenticated]


def assign_coverage(request):
    call_command('coverage_assigner')
    return HttpResponse("Coverage has been assigned")