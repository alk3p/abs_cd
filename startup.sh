#!/usr/bin/env bash

python manage.py migrate
python manage.py crontab add

if ! grep -r -i -q "debug = true" data/settings.ini; then
    echo "Starting syslog:"
    syslog-ng --no-caps
    echo "Starting crond:"
    crond -s
    echo "Starting Django:"
    #Start with bjoern
    python manage.py collectstatic --noinput
    python run.py 0.0.0.0 8000
else
    echo "WARNING: DEBUG is set to TRUE! Don't use this in production";
    python manage.py runserver 0.0.0.0:8000
fi
