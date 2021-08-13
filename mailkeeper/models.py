from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)

# Create your models here.


class Email(models.Model):
    sender = models.EmailField()
    recipient = models.EmailField()
    created = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField(blank=True)
    raw_content = models.TextField()
    inbound = models.BooleanField(default=False)
    bounced = models.BooleanField(default=False)


class User(AbstractBaseUser, PermissionsMixin):
    # Since it is not possible just to import User model from accounts app
    # this abstract model has the minimum fields to be able to use it for
    # login into django admin using old table
    class Meta:
        db_table = 'accounts_user'

    USERNAME_FIELD = 'email'

    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)

    objects = BaseUserManager()


class Outbound(Email):

    class Meta:
        proxy = True


class Inbound(Email):

    class Meta:
        proxy = True


class AuthRouter:
    # This router is to make it possible to send all auth queries to old
    # db and the rest to default one
    route_app_labels = {'admin', 'mailkeeper', 'auth'}

    def db_for_read(self, model, **hints):
        if (model._meta.app_label in self.route_app_labels and
                model._meta.db_table != 'mailkeeper_email'):
            return 'main'
        return None
