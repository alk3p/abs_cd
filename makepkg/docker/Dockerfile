FROM docker.io/archlinux/archlinux:latest
LABEL org.abs-cd.tools=makepkg
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen
RUN pacman --noconfirm -Sy archlinux-keyring && pacman-key --init && pacman-key --populate archlinux
RUN pacman-key --keyserver hkp://keyserver.ubuntu.com --recv-keys E21E057C731FE0E27BA391E79E81303CA7470095
RUN pacman-key --lsign-key E21E057C731FE0E27BA391E79E81303CA7470095
RUN systemd-machine-id-setup

RUN pacman --noconfirm -Syuq --needed base-devel devtools python
RUN useradd -m -d /build -s /bin/bash mkpkg
RUN mkdir -p /build/.gnupg
COPY privkey.asc /build/.gnupg/privkey.asc
RUN chown mkpkg:mkpkg -R /build/.gnupg
RUN chmod 700 /build/.gnupg
RUN chmod 600 /build/.gnupg/privkey.asc
USER mkpkg
RUN gpg --list-keys
RUN gpg --recv-keys E21E057C731FE0E27BA391E79E81303CA7470095
RUN gpg --import /build/.gnupg/privkey.asc
RUN gpg --list-keys
USER root
COPY sudoers /etc/sudoers
COPY pacman.conf /etc/pacman.conf
COPY makepkg.conf /etc/makepkg.conf
WORKDIR /build
VOLUME "/src"
VOLUME "/repo"
COPY run.py /run.py
ENTRYPOINT ["/run.py"]
