from django.contrib import admin
from mailkeeper.models import Email, Outbound, Inbound


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
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(inbound=True).exclude(bounced=True)


class InboundAdmin(EmailBase):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(inbound=True)


admin.site.register(Outbound, OutboundAdmin)
admin.site.register(Inbound, InboundAdmin)
