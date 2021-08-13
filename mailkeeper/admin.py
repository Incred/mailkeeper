from base64 import b64decode
import logging

from django.contrib import admin
from django.utils.html import mark_safe
from mailkeeper.models import Email, Outbound, Inbound

logger = logging.getLogger(__name__)


class EmailBase(admin.ModelAdmin):
    list_display = ('created', 'sender', 'recipient', 'subject')
    search_fields = ('sender', 'recipient', 'subject', 'body')
    readonly_fields = ('created', 'sender', 'recipient', 'subject',
                       'body', 'raw_content')
    fields = ('sender', 'recipient', 'created', 'subject', 'body')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class OutboundAdmin(EmailBase):
    readonly_fields = ('created', 'sender', 'recipient', 'subject',
                       'raw_content', 'content')
    fields = ('sender', 'recipient', 'created', 'subject', 'content')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(inbound=True).exclude(bounced=True)

    def content(self, obj):
        content = obj.body
        try:
            content = mark_safe(b64decode(content).decode())
        except Exception as exception:
            logger.error('Failed to decode body: {}'.format(exception))
        return content



class InboundAdmin(EmailBase):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(inbound=True)


admin.site.register(Outbound, OutboundAdmin)
admin.site.register(Inbound, InboundAdmin)
