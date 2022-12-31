"""
Settings Tests.
"""
from flow.settings import LOGLEVEL


def test_settings():
    assert isinstance(LOGLEVEL, str)
