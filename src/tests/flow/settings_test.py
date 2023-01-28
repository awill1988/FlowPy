"""
Settings Tests.
"""
from flowpy.settings import LOGLEVEL


def test_settings():
    assert isinstance(LOGLEVEL, str)
