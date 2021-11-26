FROM archlinux:latest
LABEL maintainer="Kate Poloziuk <polket90@gmail.com>"

RUN pacman -Syuu --noconfirm
RUN pacman -S cmake --noconfirm
RUN pacman -S gcc --noconfirm
RUN pacman -S fakeroot --noconfirm
RUN pacman -S binutils --noconfirm
RUN pacman -S sudo --noconfirm
RUN pacman -S git --noconfirm
RUN pacman -S python3 --noconfirm
RUN pacman -S python-pip --noconfirm
RUN pacman -S mariadb-libs --noconfirm
RUN pacman -S phpmyadmin --noconfirm
RUN pacman -S filebeat --noconfirm

# Install the Telegraf
#RUN pacman -S --needed --noconfirm sudo # Install sudo
#RUN useradd builduser -m # Create the builduser
#RUN passwd -d builduser # Delete the buildusers password
#RUN printf 'builduser ALL=(ALL) ALL\n' | tee -a /etc/sudoers # Allow the builduser passwordless sudo
#RUN sudo -u builduser bash -c 'cd ~ && git clone https://aur.archlinux.org/telegraf.git telegraf && cd telegraf && makepkg -s --noconfirm'
#RUN sudo -u builduser bash -c 'cd ~ && sudo pacman -U telegraf/telegraf-1.20.4-1-x86_64.pkg.tar.zst --noconfirm'

COPY requirements.txt /app/requirements.txt

WORKDIR /app
COPY . /app

RUN mkdir /usr/share/pptester/ && touch /usr/share/pptester/output.log
RUN pip install -r requirements.txt

