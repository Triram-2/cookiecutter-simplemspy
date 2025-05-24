# tests/unit/test_sample_unit.py
import pytest


# Пример простой функции для тестирования
def add_numbers(x: int, y: int) -> int:
    return x + y


# Пример асинхронной функции для тестирования (если понадобится)
async def async_subtract_numbers(x: int, y: int) -> int:
    return x - y


def test_add_numbers_sync():
    """Тестирует синхронную функцию add_numbers."""
    assert add_numbers(2, 3) == 5
    assert add_numbers(-1, 1) == 0
    assert add_numbers(0, 0) == 0


@pytest.mark.asyncio
async def test_async_subtract_numbers():
    """Тестирует асинхронную функцию async_subtract_numbers."""
    result = await async_subtract_numbers(5, 2)
    assert result == 3
    result = await async_subtract_numbers(1, 5)
    assert result == -4


# Пример теста с использованием Hypothesis (если Hypothesis будет активно использоваться)
# from hypothesis import given
# from hypothesis import strategies as st

# @given(st.integers(), st.integers())
# def test_add_numbers_hypothesis(x: int, y: int):
#     """Тестирует add_numbers с использованием Hypothesis."""
#     result = add_numbers(x, y)
#     assert result == x + y
#     # Дополнительные проверки свойств, если необходимо
#     if x != 0 and y != 0:
#         # Пример свойства: коммутативность для сложения
#         assert add_numbers(y, x) == result
