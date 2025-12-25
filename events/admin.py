from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'source_name', 'severity', 'timestamp']
    list_filter = ['severity', 'timestamp', 'event_type']
    search_fields = ['source_name', 'event_type', 'description']
    readonly_fields = ['timestamp']
