web: gunicorn autobnb.wsgi --log-file -
worker: python manage.py tick --sync-airbnb --send-daily-email