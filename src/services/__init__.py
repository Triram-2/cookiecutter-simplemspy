# src/services/__init__.py
"""
Пакет для сервисного слоя приложения.

Сервисы инкапсулируют бизнес-логику и координируют взаимодействие
между API (эндпоинтами) и слоем доступа к данным (репозиториями).

Основные задачи сервисного слоя:
1.  **Оркестрация**: Управление потоком выполнения операций, включая вызовы
    нескольких репозиториев или других сервисов.
2.  **Бизнес-логика**: Реализация специфичных для домена правил, вычислений,
    проверок (помимо базовой валидации данных, которая может быть на уровне схем).
3.  **Транзакционность**: Управление транзакциями базы данных, если операция
    включает несколько шагов, которые должны быть выполнены атомарно.
    (Хотя управление сессиями и коммитами/откатами часто делегируется
    FastAPI зависимостям и методам репозитория).
4.  **Абстракция от данных**: Предоставление API более высокоуровневого интерфейса,
    скрывающего детали реализации доступа к данным. Сервисы оперируют
    Pydantic схемами для ввода и могут возвращать либо ORM-модели, либо
    Pydantic схемы для вывода.

Рекомендации по созданию сервисов:
-   Каждый сервис обычно соответствует определенной доменной сущности или группе
    связанных операций (например, `UserService`, `OrderService`).
-   Сервисы должны быть легко тестируемыми. Зависимости (например, репозитории)
    должны передаваться в конструктор (Dependency Injection), что упрощает их
    мок во время тестирования.
-   Для стандартных CRUD-операций можно использовать `BaseService` из
    `name.services.base_service`, наследуя от него и передавая
    соответствующий репозиторий.

Пример структуры конкретного сервиса:

```python
# В файле src/services/user_service.py (пример)

from sqlalchemy.ext.asyncio import AsyncSession
# from pydantic import EmailStr # Если используется в схемах

# Предполагается, что UserRepository - это конкретная реализация BaseRepository для User
# from name.db.repositories.user_repository import UserRepository
from name.db.base_repository import BaseRepository # Или используется BaseRepository напрямую
from name.models.user_model import User # Пример модели User (нужно ее определить)
from name.schemas.user_schemas import UserCreate, UserUpdate # Пример схем (нужно их определить)
from .base_service import BaseService

# Пример определения UserRepository, если он не вынесен в отдельный файл
# class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
#     def __init__(self): # Конкретный репозиторий для User
#         super().__init__(User)
#     async def get_by_email(self, db: AsyncSession, *, email: str) -> User | None:
#         # Пример специфичного метода для репозитория
#         # return await db.execute(select(User).where(User.email == email)).scalar_one_or_none()
#         pass


class UserService(BaseService[User, UserCreate, UserUpdate, BaseRepository[User, UserCreate, UserUpdate]]):
    # Если используется конкретный UserRepository, то сигнатура будет:
    # class UserService(BaseService[User, UserCreate, UserUpdate, UserRepository]):
    # def __init__(self, user_repository: UserRepository):

    def __init__(self, user_repository: BaseRepository[User, UserCreate, UserUpdate]):
        super().__init__(user_repository)
        # self.user_repository = user_repository # Можно так, если нужен прямой доступ к специфичным методам репозитория

    async def create_user_with_specific_logic(
        self, db: AsyncSession, *, user_in: UserCreate
    ) -> User:
        # Пример специфической бизнес-логики
        # Для get_by_email нужен специфичный метод в репозитории
        # if hasattr(self.repository, 'get_by_email'):
        #     existing_user = await self.repository.get_by_email(db, email=user_in.email)
        #     if existing_user:
        #         raise ValueError("Пользователь с таким email уже существует.")

        # Вызов стандартного метода создания из BaseService (или напрямую из репозитория)
        new_user = await super().create(db, obj_in=user_in)

        # Какая-то логика после создания, например, отправка email
        # send_welcome_email(new_user.email, new_user.name) # Функция должна быть определена
        return new_user

    # ... другие кастомные методы сервиса ...
```
"""

from .base_service import BaseService

__all__ = ["BaseService"]
