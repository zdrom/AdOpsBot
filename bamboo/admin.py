from django.contrib import admin

from .models import PTO, Holidays


class PTOAdmin(admin.ModelAdmin):
    model = PTO
    list_display = ('team_member', 'coverage', 'start', 'end')


class HolidaysAdmin(admin.ModelAdmin):
    model = Holidays
    list_display = ('name', 'date')


admin.site.register(PTO, PTOAdmin)
admin.site.register(Holidays, HolidaysAdmin)
