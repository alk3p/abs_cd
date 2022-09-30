#!/usr/bin/env bash

if [ ! -f /repo/crystal.db.tar.zst ]; then
    repo-add -n /repo/crystal.db.tar.zst;
else
    # Remove old versions of packages
    repo-add -q -R /repo/crystal.db.tar.zst /repo/*.pkg.tar.zst
fi

python manage.py makemigrations
python manage.py migrate
python manage.py crontab add

echo "Starting syslog:"
syslog-ng --no-caps
echo "Starting crond:"
crond -s

if ! grep -r -i -q "debug = true" data/settings.ini; then
    #Start with gunicorn
    python manage.py collectstatic --noinput
    gunicorn --bind :8000 --workers 3 abs_cd.wsgi:application
else
    echo "WARNING: DEBUG is set to TRUE! Don't use this in production";
    python manage.py runserver 0.0.0.0:8000
fi
