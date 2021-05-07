import os
from dotenv import load_dotenv

load_dotenv()

class CeleryConfig:
    broker_url = os.getenv('REDIS_URL', 'Does not exist')
    result_backend = os.getenv('REDIS_URL', 'Does not exist')
    worker_send_task_events = True
    include = ['musicakes.tasks']

class FlaskConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'Does not exist')
