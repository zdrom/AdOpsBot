import ast
import hashlib
import hmac
import json
import pprint
import urllib.parse as urlparse
from urllib.parse import parse_qs

import requests
from decouple import config
from django.http import HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from openpyxl import load_workbook

from selenium.common.exceptions import NoSuchElementException
from slack import WebClient

from background_tasks import reply_with_preview, reply_with_stats, reply_with_template, reply_with_instructions, \
    reply_with_screenshots, router
from .models import Creative
from creative_groups.models import CreativeGroup
import logging

log = logging.getLogger("django")


@csrf_exempt
def bot(request):
    slack_client = WebClient(config('SLACK_BOT_TOKEN'))

    slack_data = json.loads(request.body)

    if slack_data.get('token') != config('SLACK_VERIFICATION_TOKEN'):
        return HttpResponse(status=403)

    if slack_data.get('type') == 'url_verification':
        return HttpResponse(content=slack_data['challenge'],
                            status=200)

    event_type = slack_data['event']['type']

    if event_type == 'message':

        event = slack_data['event']
        event_channel = slack_data['event']['channel']
        message_text = event.get('text')

        # ignore bot's own message
        if event.get('bot_id') or message_text == '' or message_text is None:

            return HttpResponse(status=200)

        elif 'stats' in message_text.lower():

            # background task
            reply_with_stats(event_channel)

            return HttpResponse(status=200)

        elif 'template' in message_text.lower():

            # background task
            reply_with_template(event_channel)

            return HttpResponse(status=200)

        else:

            # background task
            reply_with_instructions(event_channel)

            return HttpResponse(status=200)

    elif event_type == 'file_shared':

        # If a bot shared file, return 200 OK
        user_id = slack_data['event']['user_id']
        user = slack_client.users_info(user=user_id)
        user_name = user.get('user').get('real_name')

        if user['user']['is_bot']:
            return HttpResponse(status=200)

        # router(slack_data, user_name)

        router.now(slack_data, user_name)

        return HttpResponse(status=200)

    else:

        pprint.pprint(f'''

                    Neither Message nor File Shared

                    f'{request.headers}

                    f'{slack_data}

                ''')

    return HttpResponse(status=200)


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