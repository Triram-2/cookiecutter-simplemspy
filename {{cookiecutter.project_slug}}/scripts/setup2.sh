# 3. Создание виртуального окружения через uv
log "INFO: Создание виртуального окружения"
uv venv /root/{{cookiecutter.project_slug}}/.venv || { log "ERROR: Не удалось создать виртуальное окружение"; exit 1; }
log "INFO: Виртуальное окружение создано"

# 4. Синхронизация с uv.lock
log "INFO: Синхронизация с uv.lock"
cd /root/{{cookiecutter.project_slug}} && uv sync || { log "ERROR: Не удалось синхронизировать с uv.lock"; exit 1; }
log "INFO: Успешная синхронизация с uv.lock"


# 5. Создание systemd сервиса
log "INFO: Создание systemd сервиса"
cat > /etc/systemd/system/{{cookiecutter.project_slug}}.service << 'EOF'
[Unit]
Description={{cookiecutter.project_name}} Daemon
After=network.target

[Service]
ExecStart=/root/{{cookiecutter.project_slug}}/.venv/bin/python /root/{{cookiecutter.project_slug}}/src/{{cookiecutter.python_package_name}}/main.py
WorkingDirectory=/root/{{cookiecutter.project_slug}}/
Restart=always
StandardOutput=append:/root/{{cookiecutter.project_slug}}/logs/stdout
StandardError=append:/root/{{cookiecutter.project_slug}}/logs/stderr

[Install]
WantedBy=multi-user.target
EOF
log "INFO: systemd сервис создан"

# 6. Управление сервисом
log "INFO: Перезагрузка конфигурации systemd"
systemctl daemon-reload || { log "ERROR: Не удалось перезагрузить конфигурацию systemd"; exit 1; }

log "INFO: Включение сервиса parser_daemon"
systemctl enable {{cookiecutter.project_slug}} || { log "ERROR: Не удалось включить сервис"; exit 1; }

log "INFO: Перезапуск сервиса parser_daemon"
systemctl restart {{cookiecutter.project_slug}} || { log "ERROR: Не удалось перезапустить сервис"; exit 1; }

log "INFO: Установка завершена успешно"