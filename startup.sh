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
    #Start with bjoern
    python manage.py collectstatic --noinput
    python run.py 0.0.0.0 8000
else
    echo "WARNING: DEBUG is set to TRUE! Don't use this in production";
    python manage.py runserver 0.0.0.0:8000
fi
