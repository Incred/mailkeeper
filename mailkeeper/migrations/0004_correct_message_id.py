# Generated by Django 2.2.23 on 2021-09-20 05:12

from django.db.models.functions import Replace, Trim
from django.db.models import Value
from django.db import migrations


def forward(apps, schema_editor):
    Email = apps.get_model('mailkeeper', 'Email')
    Email.objects.all().update(message_id=Trim('message_id'))
    email_ids = tuple(Email.objects.filter(
        message_id__startswith='<',
        message_id__endswith='>'
    ).values_list('id', flat=True))
    Email.objects.filter(id__in=email_ids).update(
        message_id=Replace('message_id', Value('>'), Value('')))
    Email.objects.filter(id__in=email_ids).update(
        message_id=Replace('message_id', Value('<'), Value('')))

def backward(*args, **kwargs):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('mailkeeper', '0003_auto_20210902_0214'),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]