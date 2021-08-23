from django.contrib import admin
from django.template.loader import render_to_string
from django.conf.urls import url

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
    readonly_fields = ('created', 'sender', 'recipient', 'subject',
                       'raw_content', 'content')
    fields = ('sender', 'recipient', 'created', 'subject', 'content')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(inbound=True).exclude(bounced=True)

    def content(self, obj):
        return render_to_string('admin/email_content.html', {'email': obj})


class InboundAdmin(EmailBase):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(inbound=True)


admin.site.register(Outbound, OutboundAdmin)
admin.site.register(Inbound, InboundAdmin)
