import logging
from datetime import date
from xml.etree import ElementTree

import requests
from decouple import config
from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import pluralize
from slack import WebClient

log = logging.getLogger("django")


class Command(BaseCommand):
    help = 'Checks for PTO today and notifies the team if someone is OOO'

    def handle(self, *args, **options):
        key = config('BAMBOO')
        today = date.today()

        url = f'https://{key}:x@api.bamboohr.com/api/gateway.php/adtheorent/v1/time_off/whos_out?start={today}&end={today}'

        r = requests.get(url=url)

        calendar = ElementTree.fromstring(r.text)

        pto_today = []

        # Add any PTO to the PTO today list but do not include me
        for item in calendar:
            if item.attrib['type'] == 'timeOff' and item[1].text != 'Zach Romano':
                pto_today.append(item[1].text)

        if pto_today:
            is_are = '{}'.format(pluralize(len(pto_today), 'is,are'))
            person_people = '{}'.format(pluralize(len(pto_today), 'person,people'))

            message = f'*There {is_are} {len(pto_today)} {person_people} on PTO today*\n'
            for person in pto_today:
                message += f'{person}\n'
            message += '*Please keep an eye on the coverage queue!*'

            slack_client = WebClient(config('SLACK_BOT_TOKEN'))

            slack_client.chat_postMessage(channel='G1P9HPMKK', text=message)
        else:
            log.info('No PTO today')
