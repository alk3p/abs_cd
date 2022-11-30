FROM alpine:3.17
LABEL org.abs-cd=webcd_manager

RUN apk add --update --no-cache \
        cronie \
        git \
        libev \
        openssh \
        pacman \
        pkgconfig \
        py3-gitpython \
        py3-pip \
        py3-syslog-ng \
        py3-wheel \
        tini \
        zstd; \
    pacman-key --init; \
    apk add --no-cache --virtual .build-deps \
        gcc \
        libev-dev \
        musl-dev \
        pacman-dev \
        python3-dev; \
    python3 -m pip install \
        bjoern>=3.2.2 \
        Django==3.2.13 \
        django-sortable-listview==0.43 \
        django-crontab==0.7.1 \
        docker>=4.3.1 \
        pyalpm>=0.10.6; \
    apk del .build-deps; \
    sed -i 's@/var/log/cron.log@/proc/1/fd/1@g' /etc/syslog-ng/syslog-ng.conf; \
    echo -e '\n[crystal]\nServer = file:///repo\nSigLevel = Never' >> /etc/pacman.conf; \
    mkdir -p /root/.ssh; \
    echo -e 'Host github.com\n\tIdentityFile /opt/abs_cd/data/github\n\tUser git' > /root/.ssh/config; \
    ssh-keyscan -H github.com > /root/.ssh/known_hosts;

COPY abs_cd/ /opt/abs_cd/abs_cd/
COPY cd_manager/ /opt/abs_cd/cd_manager/
COPY makepkg/ /opt/abs_cd/makepkg/
COPY static/ /opt/abs_cd/static/
COPY templates/ /opt/abs_cd/templates/
COPY manage.py run.py startup.sh settings.ini.template /opt/abs_cd/

VOLUME /repo /var/packages /opt/abs_cd/data /opt/abs_cd/staticfiles

EXPOSE 8000
WORKDIR /opt/abs_cd

ENTRYPOINT ["/sbin/tini", "--", "./startup.sh"]
