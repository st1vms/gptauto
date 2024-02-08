"""Utilities"""

from time import sleep
from random import uniform


def random_sleep(_min: float, _max: float) -> None:
    """Perform a random sleep in the interval [_min, _max]"""
    sleep(round(uniform(_min, _max), 3))
