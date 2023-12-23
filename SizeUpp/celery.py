# # celery.py
# from __future__ import absolute_import, unicode_literals
# import os
# from celery import Celery

# # set the default Django settings module for the 'celery' program.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SizeUpp.settings')

# # create a Celery instance and configure it using the settings module.
# celery_app = Celery('SizeUpp')

# # Using a string here means the worker doesn't have to serialize
# # the configuration object to child processes.
# celery_app.config_from_object('django.conf:settings', namespace='CELERY')

# # Load task modules from all registered Django app configs.
# celery_app.autodiscover_tasks()
