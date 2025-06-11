#!/bin/bash

# Функция логирования в консоль
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# --- Шаг 0: Проверка прав root и определение путей ---
log "INFO: Шаг 0: Проверка прав и определение переменных..."
if [ "$EUID" -ne 0 ]; then
    log "ERROR: Скрипт должен выполняться от имени пользователя root."
    exit 1
fi

# Определяем директорию скрипта, чтобы использовать относительные пути
# Предполагается, что setup.sh находится в корне проекта.
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"
PYTHON_IN_VENV="$VENV_DIR/bin/python"
UV_IN_VENV="$VENV_DIR/bin/uv" # Предполагаемый путь к uv в venv, если он туда ставится

# Путь для pipx приложений для пользователя root
PIPX_BIN_DIR="/root/.local/bin"
UV_VIA_PIPX="$PIPX_BIN_DIR/uv"

log "INFO: Корень проекта: $PROJECT_ROOT"
log "INFO: Директория виртуального окружения: $VENV_DIR"
log "INFO: Скрипт выполняется от root."
log "INFO: Шаг 0 завершен."
echo # Пустая строка для лучшей читаемости логов

# --- Шаг 1: Обновление системы и установка системных зависимостей ---
log "INFO: Шаг 1: Обновление системы и установка системных зависимостей..."
export DEBIAN_FRONTEND=noninteractive # Избегаем интерактивных диалогов при установке

log "INFO: Обновление списка пакетов и системы..."
apt-get update -q && apt-get upgrade -y -q || { log "ERROR: Не удалось обновить систему."; exit 1; }

log "INFO: Установка основных пакетов: python3, python3-venv, python3-pip, wget, gnupg..."
apt-get install -y python3 python3-venv python3-pip wget gnupg || { log "ERROR: Не удалось установить основные пакеты."; exit 1; }

log "INFO: Установка Google Chrome..."
# Установка зависимостей Chrome (некоторые могут быть уже установлены)
apt-get install -y libxss1 libappindicator1 libindicator7 libgbm1 libnspr4 libnss3 libwayland-server0 libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0 libcairo2 libcups2 libdbus-1-3 libdrm2 libexpat1 libfontconfig1 libgcc1 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxtst6 ca-certificates fonts-liberation lsb-release xdg-utils --no-install-recommends || { log "WARN: Не удалось установить все зависимости Google Chrome, но установка продолжается."; }

wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -P /tmp/ || { log "ERROR: Не удалось скачать Google Chrome."; exit 1; }
dpkg -i /tmp/google-chrome-stable_current_amd64.deb || apt-get install -f -y && dpkg -i /tmp/google-chrome-stable_current_amd64.deb || { log "ERROR: Не удалось установить Google Chrome."; exit 1; }
rm -f /tmp/google-chrome-stable_current_amd64.deb
log "INFO: Google Chrome успешно установлен."

log "INFO: Установка pipx..."
python3 -m pip install --user --upgrade pipx || { log "ERROR: Не удалось установить pipx через pip."; exit 1; }
# Добавляем pipx в PATH для root, если его там нет.
# ensurepath для root может потребовать --force, или ручного добавления.
# Для простоты, предполагаем, что /root/.local/bin будет в PATH после перелогина или в новой сессии.
# Для текущей сессии добавим явно:
export PATH="$PIPX_BIN_DIR:$PATH" 
python3 -m pipx ensurepath --force || log "WARN: 'pipx ensurepath' завершился с предупреждением, но установка продолжается."

log "INFO: Шаг 1 завершен."
echo

# --- Шаг 2: Установка uv ---
log "INFO: Шаг 2: Установка uv через pipx..."
# Убедимся, что PATH обновлен для текущего скрипта, чтобы найти pipx
if ! command -v pipx &> /dev/null; then
    log "WARN: pipx не найден в PATH сразу после установки. Попытка использовать /root/.local/bin/pipx"
    PIPX_CMD="/root/.local/bin/pipx"
    if ! command -v $PIPX_CMD &> /dev/null; then
        log "ERROR: pipx не найден даже по полному пути. Проверьте установку pipx."
        exit 1
    fi
else
    PIPX_CMD="pipx"
fi

"$PIPX_CMD" install uv || { log "ERROR: Не удалось установить uv через pipx."; exit 1; }
# Проверяем, доступен ли uv
if ! command -v "$UV_VIA_PIPX" &> /dev/null && ! command -v uv &> /dev/null ; then
     log "ERROR: uv не найден в PATH после установки через pipx ($UV_VIA_PIPX или uv). Проверьте PATH."
     exit 1
fi
log "INFO: uv успешно установлен."
log "INFO: Шаг 2 завершен."
echo

# --- Шаг 3: Настройка проекта ---
log "INFO: Шаг 3: Настройка проекта..."
log "INFO: Создание/обновление виртуального окружения в '$VENV_DIR'..."
# Используем uv, установленный через pipx
"$UV_VIA_PIPX" venv "$VENV_DIR" --python python3 || { log "ERROR: Не удалось создать/настроить виртуальное окружение с помощью uv."; exit 1; }
log "INFO: Виртуальное окружение успешно настроено в '$VENV_DIR'."

log "INFO: Активация виртуального окружения для текущей сессии..."
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate" || {
    log "WARN: Не удалось автоматически активировать окружение. Убедитесь, что '$VENV_DIR/bin' будет в PATH для последующих команд.";
}

# Определяем команду uv для использования (из venv или глобальный от pipx)
# На данный момент uv не устанавливается внутрь venv при `uv venv`
# так что мы продолжим использовать $UV_VIA_PIPX
UV_COMMAND_FOR_PROJECT="$UV_VIA_PIPX"

if [ -f "$PROJECT_ROOT/uv.lock" ]; then
    log "INFO: Найден файл 'uv.lock'. Синхронизация зависимостей..."
    "$UV_COMMAND_FOR_PROJECT" sync --python "$PYTHON_IN_VENV" || { log "ERROR: Не удалось синхронизировать с 'uv.lock'"; exit 1; }
    log "INFO: Зависимости успешно синхронизированы с 'uv.lock'."
else
    log "INFO: Файл 'uv.lock' не найден. Установка зависимостей из 'pyproject.toml' (включая 'all')..."
    "$UV_COMMAND_FOR_PROJECT" pip install -e ".[all]" --python "$PYTHON_IN_VENV" || { log "ERROR: Не удалось установить зависимости из 'pyproject.toml'"; exit 1; }
    log "INFO: Зависимости успешно установлены из 'pyproject.toml'."
    log "INFO: Рекомендуется создать файл 'uv.lock': $UV_COMMAND_FOR_PROJECT pip freeze > uv.lock или $UV_COMMAND_FOR_PROJECT lock"
fi
log "INFO: Шаг 3 завершен."
echo

log "INFO: === Настройка проекта успешно завершена ==="
log "INFO: Не забудьте активировать виртуальное окружение в вашей сессии терминала: source $VENV_DIR/bin/activate"
log "INFO: или запускайте команды через uv из виртуального окружения, например: $PYTHON_IN_VENV -m uvicorn src.main:app"
