import gc
import os
import ctypes
import logging
from platform import system
from typing import Any, Optional
from weakref import ref, ReferenceType, proxy, ProxyType

logger = logging.getLogger("flow.memory")


def _weakref_deleted_callback(_ref: Any):
    """Invoked when referenced object is deleted"""
    logger.debug("weakref_deleted_callback(%s)", _ref)


def try_gc(attempt_os: Optional[bool] = False) -> int:
    """Manually tells the Python garbage collector to cleanup.

    Returns:
        int: the number of Python objects that were "unreachable", which is a
             standardized Python garbage collection concept.
    """
    unreachable = gc.collect()

    # if POSIX-compatible system, we'd like to reap spawned
    # resources this program is responsible for within the OS.
    if os.name == "posix" and attempt_os:
        try:
            libc = ctypes.CDLL("libc.so.6")
            libc.malloc_trim(0)
            del libc
        except Exception:  # pylint: disable=broad-except
            if system() != "Darwin":
                logger.warning("did not finish reclaiming OS memory")

    logger.debug("garbage collection [unreachable_objects=%d]", unreachable)
    return unreachable


def make_ref(obj: object) -> ReferenceType:
    """creates a weakref reference of the provided Python object.

    Args:
        obj (object): a Python object.

    Returns:
        ReferenceType: can call itself to unwrap obj.
    """
    return ref(obj, _weakref_deleted_callback)


def make_proxy(obj: object) -> ProxyType:
    """creates a weakref proxy object to the provided Python object.

    Args:
        obj (object): a Python object.

    Returns:
        ProxyType: is like a virtual representation of obj.
    """
    return proxy(obj, _weakref_deleted_callback)
