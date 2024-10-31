web: gunicorn showsecho.wsgi
worker: celery -A showsecho worker --loglevel=info --pool=solo
beat: celery -A showsecho beat --loglevel=info
