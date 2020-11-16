web: gunicorn setup:app
worker: celery -A app.celery worker --loglevel=INFO