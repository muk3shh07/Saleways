web: gunicorn --bind :8000 --workers 3 saleways.wsgi:application
release: python manage.py collectstatic --noinput 