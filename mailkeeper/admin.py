from smtplib import SMTPException

from django.core.mail import send_mail
from django.contrib import admin, messages
from django.contrib.auth.models import BaseUserManager
from django.template.loader import render_to_string
from django.conf.urls import url
from django.shortcuts import redirect

from mailkeeper.models import Email, Outbound, Inbound
from mailkeeper.forms import SendEmailForm



class EmailBase(admin.ModelAdmin):
    list_display = ('created', 'sender', 'recipient', 'subject',
                    'delivery_status', 'extended_delivery_status')
    search_fields = ('sender', 'recipient', 'subject', 'body')
    readonly_fields = ('created', 'sender', 'recipient', 'subject',
                       'body', 'raw_content')
    fields = ('sender', 'recipient', 'created', 'subject', 'body')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def delivery_status(self, obj):
        return obj.status == 'sent'
    delivery_status.boolean = True


class OutboundAdmin(EmailBase):
    readonly_fields = ('created', 'sender', 'recipient', 'subject',
                       'raw_content', 'content', 'send_email_block',
                       'delivery_status', 'extended_delivery_status')
    fields = None
    fieldsets = (
        (None, {
            'fields': (
                ('created',),
                ('sender',),
                ('recipient',),
                ('send_email_block',),
                ('delivery_status', 'extended_delivery_status'),
                ('subject',),
                ('content',),
            ),
        }),
    )
    email_form = None

    def delivery_status(self, obj):
        return obj.status == 'sent'
    delivery_status.boolean = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(inbound=True).exclude(bounced=True)

    def content(self, obj):
        return render_to_string('admin/email_content.html', {'email': obj})

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save'] = False
        extra_context['show_save_and_continue'] = False
        if not request.POST or '_send_email' not in request.POST:
            return super().change_view(request, object_id, form_url,
                                       extra_context)
        email_obj = self.get_object(request, object_id)
        email_form = SendEmailForm(request.POST)
        recipient = None
        if email_form.is_valid():
            recipient = email_form.cleaned_data['email']
        else:
            message_type = messages.ERROR
            message_text = ('Email hasn\'t been sent, check the recipient '
                            ' address.')
        self.email_form = email_form
        if recipient:
            try:
                self.send_email(recipient, email_obj)
                message_type = messages.SUCCESS
                message_text = 'Email has been sent to {}.'.format(recipient)
            except SMTPException:
                message_type = messages.ERROR
                message_text = ('Email hasn\'t been sent. Try again later.')
        return self.redirect_with_message(request, object_id, message_type,
                                          message_text)

    def redirect_with_message(self, request, obj_id, message_type,
                              message_text):
        messages.add_message(request, message_type, message_text)
        return redirect('admin:mailkeeper_outbound_change', object_id=obj_id)

    def log_change(self, request, object, message):
        pass

    def send_email_block(self, obj):
        if self.email_form:
            context = {'email_form': self.email_form}
        else:
            context = {'email_form': SendEmailForm(
                initial={'email': obj.recipient})}
        return render_to_string('admin/send_email.html', context)
    send_email_block.short_description = ('Re-send Email')

    def send_email(self, recipient, email_obj):
        send_mail(
            email_obj.subject,
            email_obj.content,
            email_obj.sender,
            [recipient],
            html_message=email_obj.body_decoded if email_obj.is_html else None
        )

class InboundAdmin(EmailBase):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(inbound=True)


admin.site.register(Outbound, OutboundAdmin)
admin.site.register(Inbound, InboundAdmin)
