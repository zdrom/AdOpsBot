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

        # Coverage is assigned for all pto that is scheduled to start within the next 5 days
        five_days_from_today = today + timedelta(days=5)

        # Get all PTO within the next two weeks
        # To check for coverage conflicts of overlapping PTO
        fifteen_days_from_now = today + timedelta(days=15)

        if today.weekday() == 5 or today.weekday() == 6:  # If it is a weekend don't check for PTO
            return

        key = config('BAMBOO')
        url = f'https://{key}:x@api.bamboohr.com/api/gateway.php/adtheorent/v1/time_off/whos_out?start={today}&end={fifteen_days_from_now}'

        #  r = requests.get(url=url, verify=False)
        r = requests.get(url=url)

        calendar = ElementTree.fromstring(r.text)

        # Check to see if someone has cancelled existing PTO
        # If a request ID exists in the PTO table but does not exist in the Bamboo API call, remove it from the list of PTO
        existing_request_ids = list(PTO.objects.filter(start__gte=today).values_list('request_id', flat=True))
        new_request_ids = []

        # Add any new PTO
        for item in calendar:

            # If the item type is TimeOff and Not Holiday, It's not for me, and the team member needs coverage
            if item.attrib['type'] == 'timeOff' and item[1].text != 'Zach Romano' and Team.objects.get(
                    name=item[1].text).needs_coverage == True:
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
            if str(request_id) not in new_request_ids and request_id != 0:
                request_ids_to_remove.append(request_id)
                print(f'*****Removing {PTO.objects.get(request_id=request_id)} because it was deleted from Bamboo')

        PTO.objects.filter(request_id__in=request_ids_to_remove).delete()

        # Get all pto that does not have coverage assigned
        # This step is separate from adding the PTO in case there are multiple new pto requests that overlap
        pto_that_needs_coverage = PTO.objects.filter(coverage=None, start__range=(today, five_days_from_today)).all()

        # If there is nothing that needs coverage, return
        if pto_that_needs_coverage.count() == 0:
            print('No PTO assignments today')
            return

        for pto in pto_that_needs_coverage:
            print(f'*****Assigning Coverage for {pto.team_member.name} from {pto.start} through {pto.end}*****')

            # Filter out the team member taking PTO and convert to a list
            # Newer employees are not eligible to cover
            eligible_for_coverage = list(
                Team.objects.filter(~Q(id=pto.team_member_id), eligible_to_cover=True).values_list(flat=True))

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
                        print(
                            f'{existing_pto.team_member.name} is not eligible for coverage because they will be on PTO')
                        if existing_pto.team_member_id in eligible_for_coverage:
                            # Check to see if the person taking PTO has been removed from the list already
                            # Maybe they took of two days in a row with separate requests
                            eligible_for_coverage.remove(existing_pto.team_member_id)

                        if existing_pto.coverage is not None:
                            # if coverage exists for the existing PTO
                            # Remove the team member who is assigned coverage
                            print(
                                f'{existing_pto.coverage.name} is not eligible for coverage because they are already assigned coverage')

                            if existing_pto.coverage_id in eligible_for_coverage:
                                # Check to see if the coverage has been removed from the list already
                                # Maybe they were assigned coverage and then took PTO later
                                eligible_for_coverage.remove(existing_pto.coverage_id)

            # assign coverage
            if len(eligible_for_coverage) == 1:

                pto.coverage = Team.objects.get(pk=eligible_for_coverage[0])
                print(f'Coverage assigned to {Team.objects.get(pk=eligible_for_coverage[0]).name} because they are the only one eligible')

            elif len(eligible_for_coverage) == 0:

                message = '*No one was eligible for coverage*\n'
                message += f' {pto.team_member} \n {pto.start} \n {pto.end}'

                slack_client.chat_postMessage(channel='C02JJ6813ME', text=message)

                return

            else:
                coverage = Team.objects.get(pk=eligible_for_coverage[0])
                print(f'Coverage assigned to {Team.objects.get(pk=eligible_for_coverage[0]).name} to start')

                for team_member_id in eligible_for_coverage:
                    team_member = Team.objects.get(pk=team_member_id)
                    if team_member.total_days_covered() < coverage.total_days_covered():
                        print(f'Coverage assigned to {team_member.name} because they have fewer days covered than {coverage.name}')
                        coverage = team_member

                pto.coverage = coverage

            pto.save()

            print('*****Total Days Covered*****')
            for member in Team.objects.all():
                print(f'{member.name}:{member.total_days_covered()}')
            print('**********')

        table = Texttable()
        table.header(['PTO', 'Start', 'End', 'Coverage'])

        for pto in pto_that_needs_coverage:
            table.add_row([pto.team_member, pto.start.strftime('%m-%d'), pto.end.strftime('%m-%d'), pto.coverage])

        message = 'There is upcoming PTO that requires coverage in the next few days.\n\nIf you are taking PTO or are assigned coverage, please remember to follow the processes outlined <https://adtheorent.atlassian.net/wiki/spaces/ADOPS/pages/2738618369/PTO+and+Coverage+Policy|here>\n\n'
        message += f'```{table.draw()}```'

        # ssl_context = ssl.create_default_context()
        # ssl_context.check_hostname = False
        # ssl_context.verify_mode = ssl.CERT_NONE

        self.client = WebClient(config('SLACK_BOT_TOKEN'))
        slack_client = self.client

        slack_client.chat_postMessage(channel='G1P9HPMKK', text=message)

        summary = '*Coverage Summary*\n\n'
        summary_table = Texttable()
        summary_table.header(['Team Member', 'Days Covered'])

        for member in Team.objects.all():
            summary_table.add_row([member.name, member.total_days_covered_this_year()])

        summary += f'```{summary_table.draw()}```'
        slack_client.chat_postMessage(channel='C02JJ6813ME', text=summary)
