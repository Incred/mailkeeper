from datetime import timedelta

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.timezone import now

from mailkeeper.models import Email


class Command(BaseCommand):
    help = 'Delete old Email objects, older than {} days'.format(
        settings.MAX_EMAIL_AGE_DAYS)

    def handle(self, *args, **options):
        date_threshold = now() - timedelta(settings.MAX_EMAIL_AGE_DAYS)
        deleted_count, _ = Email.objects.filter(
            created__lt=date_threshold).delete()
        self.stdout.write(self.style.SUCCESS('%s emails have been deleted'
                                             % deleted_count))
