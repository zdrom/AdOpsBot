import os

from django.http import HttpResponse
from decouple import config
from slack import WebClient
from slack.errors import SlackApiError


def take_screenshot(request):
    import logging
    logging.basicConfig(level=logging.DEBUG)

    slack_token = config('SLACK_BOT_TOKEN')
    client = WebClient(token=slack_token)

    try:
        response = client.chat_postMessage(
            channel="#jira_zach",
            text="Hello from your app! :tada:"
        )
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'

    return HttpResponse('OK')