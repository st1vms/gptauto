"""Utilities"""

from time import sleep
from random import uniform
from uuid import UUID


def random_sleep(_min: float, _max: float) -> None:
    """Perform a random sleep in the interval [_min, _max]"""
    sleep(round(uniform(_min, _max), 3))


def assert_uuid(text: str) -> bool:
    """Assert if `text` is a valid uuid4,
    raises ValueError in case it's not"""
    return str(UUID(text, version=4))
