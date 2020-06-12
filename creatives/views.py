from decouple import config
from django.http import HttpResponse, FileResponse
from openpyxl import load_workbook
from .models import Creative
from creative_groups.models import CreativeGroup
import logging

from slack import WebClient
from slack.errors import SlackApiError

from rest_framework import viewsets
from .serializers import CreativeSerializer

logging.basicConfig(level=logging.DEBUG)


class CreativeViewSet(viewsets.ModelViewSet):
    queryset = Creative.objects.all().order_by('name')
    serializer_class = CreativeSerializer


def save_creatives(request):
    wb = load_workbook(filename='/Users/zachromano/PycharmProjects/AdOpsBot/creatives/test.xlsx')
    ws = wb.active

    cg = CreativeGroup(name=ws['B1'].value)
    cg.save()

    for columns in ws.iter_rows(4, ws.max_row, 0, ws.max_column, True):

        logging.warning(f'Column 0: {columns[0]}')  # The creative name

        creative = Creative(name=columns[0], markup=columns[1], blocking=False, creative_group_id=cg)
        creative.save()

        creative.determine_adserver()
        creative.has_blocking()

        if creative.blocking:
            creative.remove_blocking()

        creative.take_screenshot()
        creative.save_screenshot()

    file_zip = cg.create_zip()

    # return HttpResponse('OK')

    return FileResponse(open(file_zip, 'rb'), as_attachment=True)
