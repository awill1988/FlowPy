"""
Memory Tests.
"""

import sys
from weakref import getweakrefcount
from flow.memory import try_gc, make_ref, make_proxy


class ContrivedDoNothinger:
    pass


def test_try_gc():
    assert try_gc is not None
    # this should always be greater than zero because we assume
    # because this returns the number of objects we can't clean up
    # and we assume that's always greater than zero, because it's Python!
    assert try_gc() >= 0


def test_make_ref():
    # for sanity, do garbage collection
    assert try_gc() >= 0

    # make instance of some object
    obj = ContrivedDoNothinger()

    # number of references in system for this object
    num_obj_refs = sys.getrefcount(obj)
    assert num_obj_refs > 0

    # number of weak references should begin with zero
    assert getweakrefcount(obj) == 0

    # references must unwrap and be equal to object
    ref = make_ref(obj)
    assert ref() == obj

    # number of weak references should have incremented
    assert getweakrefcount(obj) == 1

    # number of system (GC) references should be the same.
    assert sys.getrefcount(obj) == num_obj_refs

    # if we put the obj in a list, then the number of references
    # should increase
    _some_list = [obj]
    assert sys.getrefcount(obj) == (num_obj_refs + 1)

    # if we remove the list, number of references should decrement
    del _some_list
    assert sys.getrefcount(obj) == num_obj_refs

    # delete the reference
    del ref

    # number of weak references should end with zero
    assert getweakrefcount(obj) == 0


def test_make_proxy():
    # for sanity, do garbage collection
    assert try_gc() >= 0

    # make instance of some object
    obj = ContrivedDoNothinger()

    # number of references in system for this object
    num_obj_refs = sys.getrefcount(obj)
    assert num_obj_refs > 0

    # number of weak references should begin with zero
    assert getweakrefcount(obj) == 0

    # references must unwrap and be equal to object
    proxy = make_proxy(obj)
    assert proxy == obj

    # number of weak references should have incremented
    assert getweakrefcount(obj) == 1

    # number of system (GC) references should be the same.
    assert sys.getrefcount(obj) == num_obj_refs

    # if we put the obj in a list, then the number of references
    # should increase
    _some_list = [obj]
    assert sys.getrefcount(obj) == (num_obj_refs + 1)

    # if we remove the list, number of references should decrement
    del _some_list
    assert sys.getrefcount(obj) == num_obj_refs

    # delete the reference
    del proxy

    # number of weak references should end with zero
    assert getweakrefcount(obj) == 0
