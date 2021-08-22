import os

broker_url = os.environ.get('SCROOGE_BROKER_URL', 'pyamqp://user:bitnami@localhost:5672')
task_serializer = 'json'
accept_content = ['json']
timezone = 'UTC'
include = ['scrooge.tasks']
beat_schedule = {
    'update-prices-every-5-minutes': {
        'task': 'scrooge.tasks.update_prices',
        'schedule': 300.0
    },
}
