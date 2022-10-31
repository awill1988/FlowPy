import gc
import os
import ctypes
import logging
from platform import system
from weakref import ref, ReferenceType, proxy, ProxyType

logger = logging.getLogger("snotel.memory")


def try_gc() -> int:
    unreachable = gc.collect()

    if os.name == "posix":
        try:
            libc = ctypes.CDLL("libc.so.6")
            libc.malloc_trim(0)
            del libc
        except Exception:  # pylint: disable=broad-except
            if system() != "Darwin":
                logger.warning("did not finish reclaiming OS memory")
    logger.debug("garbage collection ran [unreachable_objects=%d]", unreachable)
    return unreachable


def weakref_deleted_callback(reference):
    """Invoked when referenced object is deleted"""
    logger.debug("weakref_deleted_callback(%s)", reference)


def make_ref(obj: object) -> ReferenceType:
    return ref(obj, weakref_deleted_callback)


def make_proxy(obj: object) -> ProxyType:
    return proxy(obj, weakref_deleted_callback)
