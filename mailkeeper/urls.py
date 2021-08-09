from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path(r'mailkeeper/admin/', admin.site.urls),
]
