FROM docker.io/archlinux/archlinux:base-devel
LABEL org.abs-cd.tools=makepkg

RUN set -eux; \
    echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen; \
    pacman --noconfirm -Sy archlinux-keyring && pacman-key --init && pacman-key --populate archlinux; \
    pacman-key --keyserver hkp://keyserver.ubuntu.com --recv-keys E21E057C731FE0E27BA391E79E81303CA7470095; \
    pacman-key --lsign-key E21E057C731FE0E27BA391E79E81303CA7470095; \
    systemd-machine-id-setup; \
    pacman --noconfirm -Syuq --needed devtools meson-python && rm /var/cache/pacman/pkg/*; \
    useradd -m -d /builder -s /bin/bash builder; \
    echo -e 'root ALL=(ALL) ALL\nbuilder ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers;

USER builder
RUN set -eux; \
    gpg --list-keys; rm -rf /builder/.gnupg/common.conf; \
    echo -e 'keyserver-options auto-key-retrieve' > /builder/.gnupg/gpg.conf; \
    echo -e 'keyserver hkps://keyserver.ubuntu.com' >> /builder/.gnupg/gpg.conf; \
    echo -e 'auto-key-locate hkps://keyserver.ubuntu.com' >> /builder/.gnupg/gpg.conf; \
    gpg --list-keys;

USER root
COPY makepkg.conf pacman.conf /etc/
WORKDIR /builder
VOLUME /src /repo
COPY run.py /run.py
ENTRYPOINT ["/run.py"]
