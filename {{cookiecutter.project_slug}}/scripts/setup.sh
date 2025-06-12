#!/bin/bash

# Функция логирования в консоль
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Проверка прав root
if [ "$EUID" -ne 0 ]; then
    log "ERROR: Скрипт должен выполняться от root"
    exit 1
fi

# 1. Обновление системы и установка базовых пакетов
log "INFO: Обновление системы и установка базовых пакетов"
apt update && apt upgrade -y || { log "ERROR: Не удалось обновить систему"; exit 1; }
sudo apt install -y libxss1 libappindicator1 libindicator7
sudo wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt install -y -f
sudo rm google-chrome-stable_current_amd64.deb
apt install -y python3 python3-venv python3-pip || { log "ERROR: Не удалось установить Python пакеты"; exit 1; }
apt install -y pipx
apt-get install locales
locale-gen ru_RU.UTF-8
update-locale LANG=ru_RU.UTF-8
log "INFO: Базовые пакеты успешно установлены"

# 2. Установка uv и добавление в PATH
log "INFO: Установка uv"
pipx install uv || { log "ERROR: Не удалось установить uv"; exit 1; }
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
export PATH="$HOME/.local/bin:$PATH"
pipx ensurepath
source ~/.bashrc
log "INFO: uv успешно установлен и добавлен в PATH"
reboot
