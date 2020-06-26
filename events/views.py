import logging

import pprint
from decouple import config
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from slack import WebClient
from background_tasks import reply_with_template, reply_with_instructions, reply_with_screenshots, reply_with_stats

log = logging.getLogger("django")

client = WebClient(config('SLACK_BOT_TOKEN'))


class Events(APIView):
    def post(self, request, *args, **kwargs):

        slack_client = WebClient(config('SLACK_BOT_TOKEN'))

        slack_data = request.data

        if slack_data.get('token') != config('SLACK_VERIFICATION_TOKEN'):
            return Response(status=status.HTTP_403_FORBIDDEN)

        if slack_data.get('type') == 'url_verification':

            return Response(data=slack_data,
                            status=status.HTTP_200_OK)

        event_type = slack_data['event']['type']

        if event_type == 'message':

            event = slack_data['event']
            event_channel = slack_data['event']['channel']
            message_text = event.get('text')

            # ignore bot's own message
            if event.get('bot_id') or message_text == '' or message_text is None:

                return Response(status=status.HTTP_200_OK)

            elif 'stats' in message_text.lower():

                # background task
                reply_with_stats(event_channel)

                return Response(status=status.HTTP_200_OK)

            elif 'template' in message_text.lower():

                # background task
                reply_with_template(event_channel)

                return Response(status=status.HTTP_200_OK)

            else:

                # background task
                reply_with_instructions(event_channel)

                return Response(status=status.HTTP_200_OK)

        elif event_type == 'file_shared':

            # If a bot shared file, return 200 OK
            user_id = slack_data['event']['user_id']
            user = slack_client.users_info(user=user_id)
            user_name = user.get('user').get('real_name')

            if user['user']['is_bot']:
                return Response(status=status.HTTP_200_OK)

            reply_with_screenshots(slack_data, user_name)

            return Response(status=status.HTTP_200_OK)

        else:

            pprint.pprint(f'''
            
                Neither Message nor File Shared
                
                f'{request.headers}

                f'{request.data}
            
            ''')

        return Response(status=status.HTTP_200_OK)
