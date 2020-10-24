import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Environment variables for Celery and Redies

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'Does not exist')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'Does not exist')

def make_celery(app):
	celery = Celery(
		app.import_name,
		backend=app.config['CELERY_RESULT_BACKEND'],
		broker=app.config['CELERY_BROKER_URL'],
	)

	class ContextTask(celery.Task):
		def __call__(self, *args, **kwargs):
			with app.app_context():
				return self.run(*args, **kwargs)

	celery.Task = ContextTask
	return celery