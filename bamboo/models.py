from django.db import models
from django.db.models import Q
import numpy as np



class Team(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def total_days_covered(self):

        total_days_covered = 0

        holidays = Holidays.objects.all()

        for pto in self.coverage.all():
            # Use numpy to only count weekdays
            days = np.busday_count(pto.start, pto.end) + 1
            total_days_covered += days

            # Don't include holidays in total days covered
            for holiday in holidays:
                if pto.start < holiday.date < pto.end:
                    total_days_covered -= 1

        return total_days_covered


class PTO(models.Model):
    request_id = models.IntegerField()
    team_member = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_member')
    coverage = models.ForeignKey(Team, on_delete=models.CASCADE, blank=True, null=True, related_name='coverage')
    start = models.DateField()
    end = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(f'{self.team_member.name} {self.request_id}')

    def assign_coverage(self):
        # Filter down team members to only those eligible to cover

        # remove team member who is taking the PTO
        eligible_to_cover = Team.objects.filter(~Q(id=self.team_member_id))

        # Look for overlapping PTO

        return eligible_to_cover


class Holidays(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
