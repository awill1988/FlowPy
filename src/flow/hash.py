from logging import getLogger as logger
import mmh3

_logger = "flow.memory"


def non_crypto_unsigned_int_hash(*args: str) -> int:
    """non_crypto_unsigned_int_hash

    Uses MurmurHash, a set of fast and robust non-cryptographic hash,
    resulting in unsigned 32-bit integers.

    Returns:
        int: a number that represents a simple hash of the supplied arguments
    """

    log = logger(_logger)

    # validate input: todo, better errors
    assert args is not None and len(args) > 0

    log.debug("calculating hash for {args}")

    return mmh3.hash(
        "".join(args), signed=False
    )  # pylint: disable=c-extension-no-member
