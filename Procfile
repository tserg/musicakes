web: gunicorn musicakes:app
worker: celery -A musicakes.celery_app worker --loglevel=INFO
