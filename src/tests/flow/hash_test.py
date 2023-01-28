"""
Hash Tests.
"""
from flowpy.hash import non_crypto_unsigned_int_hash


def test_non_crypto_unsigned_int_hash():
    # assert it's a method
    assert non_crypto_unsigned_int_hash is not None

    # a single argument of empty string should return nothing
    value = non_crypto_unsigned_int_hash("")
    assert value == 0

    # multiple arguments of empty strings should also return nothing
    value = non_crypto_unsigned_int_hash("", "", "", "")
    assert value == 0

    # a single argument of non-empty string should return a positive value
    value = non_crypto_unsigned_int_hash("0")
    assert value >= 0
