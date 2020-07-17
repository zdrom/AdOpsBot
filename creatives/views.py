import hashlib
import hmac
import json
import urllib.parse as urlparse
from urllib.parse import parse_qs

import requests
from decouple import config
from django.http import HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from openpyxl import load_workbook

from background_tasks import reply_with_preview
from .models import Creative
from creative_groups.models import CreativeGroup
import logging

from rest_framework import viewsets
from .serializers import CreativeSerializer

log = logging.getLogger("django")


class CreativeViewSet(viewsets.ModelViewSet):
    queryset = Creative.objects.all().order_by('name')
    serializer_class = CreativeSerializer


@csrf_exempt
def preview(request):
    if request.POST:
        if request_valid(request):

            parsed = urlparse.urlparse(request.body.decode())
            text = parse_qs(parsed.path)['text'][0]
            user = parse_qs(parsed.path)['user_name'][0]
            response_url = parse_qs(parsed.path)['response_url'][0]

            reply_with_preview(text, user, response_url)
            return HttpResponse(status=200)


def request_valid(request):
    # confirm that the request is from slack
    signing_secret = config('SLACK_SIGNING_SECRET')
    signing_secret_in_bytes = bytes(signing_secret, "utf-8")
    request_body = request.body.decode()
    request_timestamp = request.headers.get('X-Slack-Request-Timestamp')
    basestring = f'v0:{request_timestamp}:{request_body}'.encode('utf-8')
    my_signature = 'v0=' + hmac.new(signing_secret_in_bytes, basestring, hashlib.sha256).hexdigest()

    slack_signature = request.headers.get('X-Slack-Signature')

    if hmac.compare_digest(my_signature, slack_signature):
        return True
    else:
        print("Verification failed. Signature invalid.")
        return False
