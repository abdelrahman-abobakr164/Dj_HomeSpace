from celery import Celery
from celery.schedules import crontab
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "home_space.settings")

app = Celery("home_space")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.timezone = "Africa/Cairo"

app.conf.beat_schedule = {
    "update-property-availability": {
        "task": "core.tasks.update_property_availability",
        "schedule": crontab(hour=6, minute=0),
    }
}
