# project_name/celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'craft_catalogue.settings')

app = Celery('craft_catalogue')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure Celery Beat schedule to run every minute
app.conf.beat_schedule = {
    'clear-expired-cart-items-every-minute': {
        'task': 'catalogue.tasks.clear_expired_cart_items',
        'schedule': 60.0,  # every 60 seconds
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
