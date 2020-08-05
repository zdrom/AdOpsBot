from django.contrib import admin
from.models import Creative


class CreativeAdmin(admin.ModelAdmin):
    model = Creative
    search_fields = ['adserver', 'blocking_vendor']
    list_display = ('name', 'adserver', 'blocking_vendor', 'width', 'height', 'placement_id', 'requested_by', 'creative_group_id', 'created_at')


admin.site.register(Creative, CreativeAdmin)
