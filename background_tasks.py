import datetime
import logging
import math
import pprint
import tempfile
import urllib
from zipfile import ZipFile, BadZipFile

import requests
from decouple import config
from django.core.files.storage import default_storage
from openpyxl import load_workbook
from slack import WebClient
from django.conf import settings
from django.db import IntegrityError

from creative_groups.models import CreativeGroup
from creatives.models import Creative
from background_task import background

slack_client = WebClient(config('SLACK_BOT_TOKEN'))

log = logging.getLogger("django")


@background(schedule=1)
def reply_with_instructions(channel):

    slack_client.chat_postMessage(
        channel=channel,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ('Hello! To get started, you\'ll need a template. '
                             'If you don\'t have one, respond with _template_\n'
                             )
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ('If you have the template already, upload it. '
                             'There is a column for *name* (name each creative something unique), '
                             'and a column for *ad tag*. Make sure when copying the ad tags into the '
                             'template that you don\'t accidentally add any other characters. '
                             'Excel likes to reformat tags sometimes.'
                             )
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ('Don\'t worry about whether or not the'
                             ' tags have blocking. I automatically remove blocking scripts before taking '
                             ' screenshots. I\'ll upload the results here when I\'m done. Shouldn\'t '
                             'take _too_ long\n'
                             )
                }
            }
        ]
    )


@background(schedule=1)
def reply_with_template(channel):
    slack_client.chat_postMessage(channel=channel, text='Here ya go!')

    # response = slack_client.files_remote_add(external_id='screenshot_template',
    #                               external_url=f'{settings.MEDIA_ROOT}/template.xlsx',
    #                               title='Template')
    #
    # print(response)

    slack_client.files_remote_share(channels=channel, file='F015JDNQWSH')


@background(schedule=1)
def reply_with_screenshots(request_data):

    file_info = slack_client.files_info(file=request_data['event']['file_id'])

    channel_list = list(file_info['file']['shares']['private'].keys())
    channel = channel_list[0]

    slack_client.chat_postMessage(channel=channel, text='Confirming receipt. Be back soon.')

    file_url = file_info['file']['url_private']

    r = requests.get(file_url, headers={'Authorization': 'Bearer %s' % config('SLACK_BOT_TOKEN')})
    r.raise_for_status

    temp = tempfile.TemporaryFile(mode='w+b')

    temp.write(r.content)

    try:

        wb = load_workbook(filename=temp)

    except IOError:

        '''
        
        If a user uploads a file that doesnt work 
        e.g. the incorrect template
        respond with the correct template
        
        '''

        slack_client.chat_postMessage(channel=channel,
                                      text="hmmmm I had trouble processing the uploaded file. "
                                           "Are you sure you used the correct template?"
                                           " To confirm, try again using the one attached below")

        slack_client.files_remote_share(channels=channel,
                                        file='F015JDNQWSH')

        return

    temp.close()

    ws = wb.active

    if ws['B1'].value is None:
        campaign_name = 'campaign'
    else:
        campaign_name = ws['B1'].value

    cg = CreativeGroup(name=campaign_name)
    cg.save()

    errors = []

    for columns in ws.iter_rows(4, ws.max_row, 0, ws.max_column, True):

        try:

            creative = Creative(name=columns[0], markup=columns[1], creative_group_id=cg)
            creative.save()

            log.info(f'successfully Created: {creative.name}')

        except IntegrityError:

            log.exception(f'Error Saving Creative: {creative.name}')

        creative.determine_adserver()
        creative.has_blocking()

        if creative.blocking:
            creative.remove_blocking()

        creative.take_screenshot()

        ''' 
        Save_image returns the creative name if there is an error
        push the creative name to an list to return to the user if there are errors
        '''

        creative_name = creative.save_image()

        if creative_name is not None:
            errors.append(creative_name)

    zip_path = f"{settings.MEDIA_ROOT}/zips/{urllib.parse.quote_plus(cg.name)}_{datetime.datetime.now().strftime('%m.%d.%H.%M')}.zip"

    try:

        with ZipFile(zip_path, 'w',) as file:

            i = 1

            for creative in cg.creative_set.all():

                # If the screenshot image was not saved successfully
                # Do not try to add it to the zip

                try:

                    if f'{creative.name}.png' in file.namelist():
                        file.write(creative.screenshot.path, arcname=f'{creative.name}_{i}.png')
                        i += 1

                    else:
                        file.write(creative.screenshot.path, arcname=f'{creative.name}.png')

                except ValueError:
                    log.error(f'Skipping over {creative.name} because there was no screenshot file')
    except BadZipFile:

        log.exception(msg='Bad Zip File found')

    slack_client.files_upload(channels=channel, file=zip_path)

    if errors:
        slack_client.chat_postMessage(channel=channel,
                                      text=f"I had some issues taking screenshots for the following creatives\n"
                                           f"{pprint.pprint(errors)}\n"
                                           f"Try uploading the template again with the creatives that didnt work."
                                           f"If you receive this message again, "
                                           f"try taking them manually by going to a tag "
                                           f"tester like https://www.cs.iupui.edu/~ajharris/webprog/jsTester.html\n"
                                           f"Sorry for the inconvenience!")

