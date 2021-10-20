uwsgi --http :5000 --wsgi-file web.py --callable app --daemonize log.txt
