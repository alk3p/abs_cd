FROM archlinux:base-devel
LABEL org.abs-cd.tools=makepkg

RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen; \
    pacman --noconfirm -Sy archlinux-keyring && pacman-key --init && pacman-key --populate archlinux; \
    pacman-key --keyserver hkp://keyserver.ubuntu.com --recv-keys E21E057C731FE0E27BA391E79E81303CA7470095; \
    pacman-key --lsign-key E21E057C731FE0E27BA391E79E81303CA7470095; \
    systemd-machine-id-setup; \
    pacman --noconfirm -Syuq --needed devtools python && rm /var/cache/pacman/pkg/*; \
    useradd -m -d /build -s /bin/bash mkpkg; \
    echo -e 'root ALL=(ALL) ALL\nmkpkg ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers; \
    mkdir -p /build/.gnupg; \
    chown mkpkg:mkpkg -R /build/.gnupg; \
    chmod 700 /build/.gnupg;

COPY makepkg.conf pacman.conf /etc/
COPY --chown=mkpkg:mkpkg privkey.asc /build/.gnupg/privkey.asc

USER mkpkg
RUN gpg --list-keys; \
    gpg --recv-keys E21E057C731FE0E27BA391E79E81303CA7470095; \
    gpg --import /build/.gnupg/privkey.asc; \
    gpg --list-keys;

USER root
WORKDIR /build
VOLUME /src /repo
COPY run.py /run.py
ENTRYPOINT ["/run.py"]
