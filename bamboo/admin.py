from django.contrib import admin

from .models import PTO, Holidays, Team


class TeamAdmin(admin.ModelAdmin):
    model = Team
    list_display = ('name',)


class PTOAdmin(admin.ModelAdmin):
    model = PTO
    list_display = ('team_member', 'coverage', 'start', 'end')


class HolidaysAdmin(admin.ModelAdmin):
    model = Holidays
    list_display = ('name', 'date')


admin.site.register(PTO, PTOAdmin)
admin.site.register(Holidays, HolidaysAdmin)
admin.site.register(Team, TeamAdmin)
