import hashlib
import hmac
import json
import re
import urllib.parse as urlparse
from urllib.parse import parse_qs

from decouple import config
from django.core import serializers
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import authentication, permissions

from slack import WebClient, errors
from slackeventsapi import SlackEventAdapter

from background_tasks import reply_with_preview, reply_with_stats, reply_with_template, reply_with_instructions, \
    router, reply_with_click_through
import logging

from creatives.models import Creative
from creatives.serializers import CreativeSerializer

log = logging.getLogger("django")


def home(request):
    return HttpResponse(status=200, content=':)')


@csrf_exempt
def bot(request):

    try:

        print(f'''
        headers: {request.headers}
        __________
        body: {request.body}
        __________
        __________
        ''')

        slack_client = WebClient(config('SLACK_BOT_TOKEN'))

        slack_data = json.loads(request.body)

        if slack_data.get('token') != config('SLACK_VERIFICATION_TOKEN'):
            print('forbidden')
            return HttpResponse(status=403)

        if slack_data.get('type') == 'url_verification':
            print('url verification')
            return HttpResponse(content=slack_data['challenge'],
                                status=200)

        event = slack_data['event']

        if event.get('subtype') == 'message_changed' or event.get('subtype') == 'message_deleted':  # Filter out an message changes
            return HttpResponse(status=200)

        ''' 
        if the event is message
        the user id is passed as user
        if it's a file shared
        the user id is passed as user_id
        get the name of the user and filter out any messages from adops
        so i'm not responding to bot messages
        '''

        try:
            if slack_data['event']['type'] == 'message':
                user_id = slack_data['event']['user']
            else:
                user_id = slack_data['event']['user_id']
        except KeyError:
            logging.exception(slack_data)

        user = slack_client.users_info(user=user_id)
        user_name = user.get('user').get('real_name')

        if user_name != 'adops':

            print('Passed All Tests')

            event_type = event['type']

            if event_type == 'message':

                event_channel = slack_data['event']['channel']
                message_text = event.get('text')

                if message_text.lower() == '':
                    print('Returning due to blank message')
                    return HttpResponse(status=200)

                if 'stats' in message_text.lower():

                    # background task
                    reply_with_stats(event_channel)

                elif 'template' in message_text.lower():

                    # background task
                    reply_with_template(event_channel)

                else:

                    # background task
                    reply_with_instructions(event_channel)

            elif event_type == 'file_shared':
                router(slack_data, user_name)

        else:
            print('Classified as a bot message')

        return HttpResponse(status=200, content='Confirming Receipt')

    except Exception as e:
        log.exception('There was an exception')
        print(f'''
        The Request Header is:
        {request.headers}
        And the Body is:
        {request.body}
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


@csrf_exempt
def get_click_through(request):
    if request.POST:
        if request_valid(request):
            parsed = urlparse.urlparse(request.body.decode())
            text = parse_qs(parsed.path)['text'][0]
            user = parse_qs(parsed.path)['user_name'][0]
            response_url = parse_qs(parsed.path)['response_url'][0]

            reply_with_click_through(text, user, response_url)
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


class CreativeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Creative.objects.all()
    serializer_class = CreativeSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['POST',])
@permission_classes((permissions.AllowAny,))
def add_macros(request):

    c = Creative(
        markup=request.data['markup']
    )

    c.determine_adserver()
    c.add_macros()

    return Response(status=200, data={"message": "Got some data!", "markup with macros": c.markup_with_macros})


@api_view(['POST',])
@permission_classes((permissions.AllowAny,))
def remove_blocking(request):

    c = Creative(
        markup=request.data['markup']
    )

    c.determine_adserver()
    c.has_blocking()
    c.remove_blocking()

    return Response(status=200, data={"markup": c.markup_without_blocking})


@api_view(['POST',])
@permission_classes((permissions.AllowAny,))
def take_screenshot(request):

    c = Creative(
        markup=request.data['markup']
    )

    c.determine_adserver()
    c.has_blocking()
    c.remove_blocking()
    c.take_screenshot()
    c.save_image()

    return Response(status=200, data={"markup": c.screenshot})


@api_view(['POST',])
@permission_classes((permissions.AllowAny,))
def generate_template(request):

    selected_range = json.loads(request.data['range'])

    # Save the header row and then remove it so that the selected range is just the tags
    headers = selected_range[0]
    selected_range.pop(0)
    placements = selected_range

    header_cols = assign_header_cols(headers)

    output = []

    for placement in placements:

        values = find_values(header_cols, placement)

        c = Creative(
            name=values['name'],
            width=values['width'],
            height=values['height'],
            placement_id=values['placement id'],
            placement_name=values['placement name'],
            markup=values['markup'],
            free_field=values['free'],
            concept=values['concept']
        )

        c.determine_adserver()
        c.add_macros()
        c.save()

        output.append(c)

    return Response(status=200, data={"placements": serializers.serialize('json', output, fields=('name', 'width', 'height', 'placement_name', 'markup_with_macros'))}, content_type='application/json')


def assign_header_cols(headers):
    header_dict = {}
    for header in headers:
        if header.lower() == 'placement id'\
                or header.lower() == 'placement_id'\
                or header.lower() == 'agency placement id':
            header_dict['placement id'] = headers.index(header)
        elif header.lower() == 'placement name'\
                or header.lower() == '* placement name'\
                or header.lower() == 'placementname'\
                or header.lower() == 'agency placement name':
            header_dict['placement name'] = headers.index(header)
        elif header.lower() == 'placement width':
            header_dict['width'] = headers.index(header)
        elif header.lower() == 'placement height':
            header_dict['height'] = headers.index(header)
        elif header.lower() == 'dimensions':
            header_dict['dimensions'] = headers.index(header)
        elif header.lower() == 'javascript tag'\
                or header.lower() == 'js_https'\
                or header.lower() == 'blocking javascript tag'\
                or header.lower() == 'script | secured'\
                or header.lower() == 'placement tag':
            header_dict['markup'] = headers.index(header)
        elif header.lower() == 'concept':
            header_dict['concept'] = headers.index(header)
        elif header.lower() == 'free':
            header_dict['free'] = headers.index(header)

    return header_dict


def find_values(header_cols, placement):
    value_dict = {}

    # Tag sheets either have dimensions as one col or as separate width and height cols
    if 'dimensions' in header_cols:
        regex = '([0-9]{3,4})\D*([0-9]{2,4})'
        matches = re.search(regex, placement[header_cols['dimensions']])
        width = matches.group(1)
        height = matches.group(2)

    # Check to see if the optional free and concept cols are present and add to the name if they are
    if 'concept' in header_cols and 'free' in header_cols:
        name = f"{width}x{height}||{placement[header_cols['concept']]}||{placement[header_cols['free']]}||{placement[header_cols['placement id']]}"
    elif 'concept' in header_cols:
        name = f"{width}x{height}||{placement[header_cols['concept']]}||{placement[header_cols['placement id']]}"
    elif 'free' in header_cols:
        name = f"{width}x{height}||{placement[header_cols['free']]}||{placement[header_cols['placement id']]}"

    markup = placement[header_cols['markup']]
    placement_name = placement[header_cols['placement name']]
    placement_id = placement[header_cols['placement id']]

    if 'free' in header_cols:
        free = placement[header_cols['free']]
    else:
        free = None

    if 'concept' in header_cols:
        concept = placement[header_cols['concept']]
    else:
        concept = None

    value_dict = {
        'name': name,
        'width': width,
        'height': height,
        'markup': markup,
        'placement name': placement_name,
        'placement id': placement_id,
        'free': free,
        'concept': concept
    }

    return value_dict
