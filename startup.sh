#! /bin/bash
# Start-up script for the server.
# Runs on Guincorn with 32 workers.
# The default port is 4080.

/usr/bin/redis-server
/usr/bin/env python2.7 init_redis.py
nohup gunicorn --access-logfile /tmp/flask-access.log --error-logfile /tmp/flask-error.log --bind 0.0.0.0:80 --workers 32 server:app &
