# locustfile.py
"""
Файл для определения сценариев нагрузочного тестирования с использованием Locust.

Этот файл должен быть заполнен пользователем шаблона для моделирования
поведения пользователей и нагрузки на конкретные эндпоинты API.

Документация Locust: https://docs.locust.io/

Пример простого Locust-файла:

from locust import HttpUser, task, between

class MyUser(HttpUser):
    # Время ожидания между выполнением задач для одного пользователя (в секундах)
    wait_time = between(1, 5)  # Случайное ожидание от 1 до 5 секунд

    # Адрес хоста (например, http://localhost:8000), который будет тестироваться.
    # Его можно также указать при запуске Locust через параметр --host.
    # host = "http://localhost:8000" 

    @task(1) # (1) - это вес задачи, если их несколько
    def get_health_check(self):
        """Проверяет эндпоинт /api/v1/health."""
        self.client.get("/api/v1/health")

    # @task(2) # Пример другой задачи с большим весом
    # def get_another_endpoint(self):
    #     self.client.get("/api/v1/some_other_endpoint")

    # def on_start(self):
    #     """ Вызывается при старте каждого виртуального пользователя (если нужно, например, для логина). """
    #     pass

    # def on_stop(self):
    #     """ Вызывается при остановке каждого виртуального пользователя (если нужно, например, для логаута). """
    #     pass

# Для запуска Locust:
# 1. Убедитесь, что locust установлен (pip install locust).
# 2. Запустите ваше FastAPI приложение.
# 3. В терминале выполните: locust -f locustfile.py --host=http://localhost:8000
#    (или используйте `make locust ARGS="--host=http://localhost:8000"`)
# 4. Откройте веб-интерфейс Locust (обычно http://localhost:8089) для настройки и запуска теста.
"""

from locust import HttpUser, task, between

# Заглушка: Пользователь должен определить свои классы пользователей и задачи здесь.
# Раскомментируйте и адаптируйте пример выше или создайте свои собственные классы.

# class WebsiteUser(HttpUser):
#     wait_time = between(1, 5)
#
#     @task
#     def index_page(self):
#         self.client.get("/") # Пример запроса к главной странице
#
#     @task
#     def health_check(self):
#         self.client.get("/api/v1/health")


if __name__ == "__main__":
    # Этот блок позволяет запустить Locust программно, если это необходимо,
    # но обычно Locust запускается из командной строки.
    # import os
    # os.system("locust -f locustfile.py --host=http://localhost:8000")
    print("Этот файл предназначен для использования с Locust.")
    print("Пример запуска: locust -f locustfile.py --host=http://your-app-host.com")
    print("Или через Makefile: make locust ARGS=\"--host=http://your-app-host.com\"")
