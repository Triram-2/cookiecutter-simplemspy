"""
Application service layer package.

Services encapsulate business logic and coordinate interactions
between the API (endpoints) and the data access layer (repositories).

Key responsibilities:
- Orchestration: Managing operation flows.
- Business Logic: Implementing domain-specific rules and calculations.
- Transaction Management: Handling database transactions if needed.
- Data Abstraction: Providing a high-level interface to the API.

Services typically use Pydantic schemas for input and can return ORM models
or Pydantic schemas for output. Dependencies (like repositories) should be
injected for testability. `BaseService` provides common CRUD operations.
"""

from .base_service import BaseService

__all__ = ["BaseService"]
