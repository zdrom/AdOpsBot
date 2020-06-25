import datetime
import logging
import os
import pprint
import tempfile
import urllib
from zipfile import ZipFile, BadZipFile

import requests
from decouple import config
from openpyxl import load_workbook
from slack import WebClient
from django.conf import settings
from django.db import IntegrityError

from creative_groups.models import CreativeGroup
from creatives.models import Creative
from background_task import background, exceptions

slack_client = WebClient(config('SLACK_BOT_TOKEN'))

log = logging.getLogger("django")


@background(schedule=1)
def reply_with_instructions(channel):
    slack_client.chat_postMessage(
        channel=channel,
        text="Hello!\n\n"
             "To get started, you\'ll need a template. "
             "If you don\'t have one, respond with _template_\n\n"
             "If you have the template already, fill it out and upload it. "
             "There are columns for:\n\n"
             "*Name* (name each creative something unique)\n\n"
             "and\n\n"
             "*Ad Tag*\n\n"
             "Make sure when copying the ad tags into the "
             "template that you don\'t accidentally add any other characters. "
             "Excel likes to reformat tags sometimes.\n\n"
             "Don\'t worry about whether or not the"
             " tags have blocking. I automatically remove blocking scripts before taking "
             "screenshots. I\'ll upload the results here when I\'m done.\n\n"
             "Shouldn\'t take _too_ long\n"
    )

    log.info('Responded with instructions')


@background(schedule=1)
def reply_with_template(channel):
    slack_client.chat_postMessage(channel=channel, text='Here ya go!')

    slack_client.files_upload(channels=channel, file=os.path.join(settings.MEDIA_ROOT, 'templates/template.xlsx'))

    log.info('Responded with the template')


@background(schedule=1)
def reply_with_screenshots(request_data):
    try:

        file_info = slack_client.files_info(file=request_data['event']['file_id'])

        channel_list = list(file_info['file']['shares']['private'].keys())
        channel = channel_list[0]

        file_url = file_info['file']['url_private']

        r = requests.get(file_url, headers={'Authorization': 'Bearer %s' % config('SLACK_BOT_TOKEN')})
        r.raise_for_status

        temp = tempfile.TemporaryFile(mode='w+b')

        temp.write(r.content)

        try:

            wb = load_workbook(filename=temp)

            slack_client.chat_postMessage(channel=channel, text='Confirming receipt. Be back soon.')
            progress_meter = slack_client.chat_postMessage(channel=channel, text='◻︎◻︎◻︎◻︎◻︎◻︎◻︎◻︎◻︎◻︎')

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

        except BadZipFile:
            log.error('Bad Zip File')

        temp.close(

        )

        ws = wb.active

        if ws['B1'].value is None:
            campaign_name = 'campaign'
        else:
            campaign_name = ws['B1'].value

        cg = CreativeGroup(name=campaign_name)
        cg.save()

        errors = []

        # Progress Meter
        p = 1

        def progress(current_creative, max_creatives):

            status = round(current_creative / max_creatives * 10)

            complete = '◼︎'
            to_do = '◻︎'

            progress_display = f'{complete * status}{to_do * (10 - status)}'

            return progress_display

        for columns in ws.iter_rows(4, ws.max_row, 0, ws.max_column, True):

            # Start the progress meter
            meter = progress(p, ws.max_row)
            slack_client.chat_update(channel=channel, ts=progress_meter['ts'], text=meter)
            p += 1
            # End the progress meter

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

        with ZipFile(zip_path, 'w', ) as file:

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


        slack_client.chat_delete(channel=channel, ts=progress_meter['ts'])  # Delete the progress meter once done
        slack_client.files_upload(channels=channel, file=zip_path)  # Upload the zip

        if errors:
            slack_client.chat_postMessage(channel=channel,
                                          text=f"I had some issues taking screenshots for the following creatives\n"
                                               f"{errors}\n"
                                               f"Try uploading the template again with the creatives that didnt work."
                                               f"If you receive this message again, "
                                               f"try taking them manually by going to a tag "
                                               f"tester like https://www.cs.iupui.edu/~ajharris/webprog/jsTester.html\n"
                                               f"Sorry for the inconvenience!")

    except exceptions.InvalidTaskError:
        log.exception('There was an issue with a background task')
