import os
from typing import Any

from celery import Celery, signals
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')


@signals.setup_logging.connect
def on_celery_setup_logging(**kwargs: Any) -> None:
    """Make all celery logs be done through our LOGGING config in settings."""


app = Celery('core')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(packages=settings.INSTALLED_APPS)
