from django.http import HttpResponse
from openpyxl import load_workbook
from .models import Creative
from creative_groups.models import CreativeGroup
import logging


logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


def save_creatives(request):
    wb = load_workbook(filename='/Users/zachromano/PycharmProjects/AdOpsBot/creatives/test.xlsx')
    ws = wb.active

    cg = CreativeGroup(name=ws['B1'].value)
    cg.save()

    for columns in ws.iter_rows(4, ws.max_row, 0, ws.max_column, True):

        logging.debug(f'Column 0: {columns[0]}')  # The creative name

        creative = Creative(name=columns[0], markup=columns[1], blocking=False, creative_group_id=cg)
        creative.save()
        creative.take_screenshot()
        creative.save_screenshot()

    cg.create_zip()

    return HttpResponse('OK')
