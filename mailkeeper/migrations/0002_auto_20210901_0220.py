# Generated by Django 2.2.23 on 2021-09-01 02:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailkeeper', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='email',
            name='message_id',
            field=models.EmailField(blank=True, max_length=254),
        ),
    ]
