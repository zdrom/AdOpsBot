from rest_framework import viewsets, permissions

from bamboo.models import PTO
from bamboo.serializers import PTOSerializer


class PTOViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = PTO.objects.all()
    serializer_class = PTOSerializer
    permission_classes = [permissions.IsAuthenticated]
