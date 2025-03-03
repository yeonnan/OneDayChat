import os
from celery import Celery
from django.conf import settings


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "onedaychat.settings")
app = Celery("onedaychat")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()