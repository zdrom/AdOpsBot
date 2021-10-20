import logging
import ssl
from datetime import date, datetime, timedelta
from xml.etree import ElementTree

import requests
from decouple import config
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.template.defaultfilters import pluralize
from slack import WebClient
from texttable import Texttable

from bamboo.models import PTO, Team

log = logging.getLogger("django")


class Command(BaseCommand):
    help = 'Assigns coverage for PTO'

    def handle(self, *args, **options):
        today = date.today()
        three_days_from_today = today + timedelta(days=3)

        if today.weekday() == 5 or today.weekday() == 6:  # If it is a weekend don't check for PTO
            return

        key = config('BAMBOO')
        url = f'https://{key}:x@api.bamboohr.com/api/gateway.php/adtheorent/v1/time_off/whos_out?start={today}&end={three_days_from_today}'

        r = requests.get(url=url)

        calendar = ElementTree.fromstring(r.text)

        # Check to see if someone has cancelled existing PTO
        # If a request ID exists in the PTO table but does not exist in the Bamboo API call, remove it from the list of PTO
        existing_request_ids = list(PTO.objects.filter(start__gte=today).values_list('request_id', flat=True))
        new_request_ids = []

        # Add any new PTO
        for item in calendar:
            if item.attrib['type'] == 'timeOff' and item[1].text != 'Zach Romano':
                # Unique ID issued by Bamboo for each request
                request_id = item[0].attrib['id']
                team_member_taking_pto = item[1].text
                start = datetime.strptime(item[2].text, '%Y-%m-%d').date()
                end = datetime.strptime(item[3].text, '%Y-%m-%d').date()

                new_request_ids.append(request_id)

                pto = PTO.objects.update_or_create(
                    request_id=request_id,
                    defaults={
                        'start': start,
                        'end': end,
                        'team_member': Team.objects.filter(name=team_member_taking_pto).first()
                    }
                )

        request_ids_to_remove = []
        for request_id in existing_request_ids:
            if str(request_id) not in new_request_ids:
                request_ids_to_remove.append(request_id)
                log.info(f'*****Removing {PTO.objects.get(request_id=request_id)} because it was deleted from Bamboo')

        PTO.objects.filter(request_id__in=request_ids_to_remove).delete()

        # Get all pto that does not have coverage assigned
        # This step is separate from adding the PTO in case there are multiple new pto requests that overlap
        pto_that_needs_coverage = PTO.objects.filter(coverage=None).all()

        # If there is nothing that needs coverage, return
        if pto_that_needs_coverage.count() == 0:
            log.info('No PTO assignments today')
            return

        for pto in pto_that_needs_coverage:

            log.info(f'*****Assigning Coverage for {pto.team_member.name} from {pto.start} through {pto.end}*****' )

            # Filter out the team member taking PTO and convert to a list
            eligible_for_coverage = list(Team.objects.filter(~Q(id=pto.team_member_id)).values_list(flat=True))

            # Get all existing PTO and check for overlaps
            all_pto = PTO.objects.filter(end__gte=date.today()).filter(~Q(request_id=pto.request_id))

            # If no existing PTO, carry on
            if len(all_pto) > 0:
                for existing_pto in all_pto:
                    latest_start = max(pto.start, existing_pto.start)
                    earliest_end = min(pto.end, existing_pto.end)
                    delta = (earliest_end - latest_start).days + 1
                    overlap = max(0, delta)

                    if overlap != 0:
                        # Remove the team member who is taking the existing PTO
                        log.info(
                            f'{existing_pto.team_member.name} is not eligible for coverage because they will be on PTO')
                        if existing_pto.team_member_id in eligible_for_coverage:
                            # Check to see if the person taking PTO has been removed from the list already
                            # Maybe they took of two days in a row with seperate requests
                            eligible_for_coverage.remove(existing_pto.team_member_id)

                        if existing_pto.coverage is not None:
                            # if coverage exists for the existing PTO
                            # Remove the team member who is assigned coverage
                            log.info(
                                f'{existing_pto.coverage.name} is not eligible for coverage because they are already assigned coverage')
                            eligible_for_coverage.remove(existing_pto.coverage_id)

            # assign coverage
            if len(eligible_for_coverage) == 1:

                pto.coverage = Team.objects.get(pk=eligible_for_coverage[0])
                log.info(f'Coverage assigned to {Team.objects.get(pk=eligible_for_coverage[0]).name} because they are the only one eligible')

            else:
                coverage = Team.objects.get(pk=eligible_for_coverage[0])
                log.info(f'Coverage assigned to {Team.objects.get(pk=eligible_for_coverage[0]).name} to start')

                for team_member_id in eligible_for_coverage:
                    team_member = Team.objects.get(pk=team_member_id)
                    if team_member.total_days_covered() < coverage.total_days_covered():
                        log.info(f'Coverage assigned to {team_member.name} because they have fewer days covered than {coverage.name}')
                        coverage = team_member

                pto.coverage = coverage

            pto.save()

            log.info('*****Total Days Covered*****')
            for member in Team.objects.all():
                log.info(f'{member.name}:{member.total_days_covered()}')
            log.info('**********')

        table = Texttable()
        table.header(['PTO', 'Start', 'End', 'Coverage'])

        for pto in pto_that_needs_coverage:
            table.add_row([pto.team_member, pto.start.strftime('%m-%d'), pto.end.strftime('%m-%d'), pto.coverage])

        message = 'Good morning!\nThere is upcoming PTO that requires coverage in the next few days.\nIf you are taking PTO please remember to do the following:\n' \
                  '1. Coordinate with your coverage\n2. Create a coverage document\n3. Notify your alignment of your coverage\n' \
                  'Please see below for the coverage assignments\n'
        message += f'```{table.draw()}```'

        # ssl_context = ssl.create_default_context()
        # ssl_context.check_hostname = False
        # ssl_context.verify_mode = ssl.CERT_NONE

        slack_client = WebClient(config('SLACK_BOT_TOKEN'))
        slack_client.chat_postMessage(channel='C02JJ6813ME', text=message)

        summary = '*Coverage Summary*\n\n'
        summary_table = Texttable()
        summary_table.header(['Team Member', 'Days Covered'])

        for member in Team. objects.all():
            summary_table.add_row([member.name, member.total_days_covered()])

        summary += f'```{summary_table.draw()}```'

        slack_client.chat_postMessage(channel='C02JJ6813ME', text=summary)