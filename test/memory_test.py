import unittest
from flow.memory import make_ref, make_proxy, try_gc
import sys

class ExpensiveObject:
    pass


class MemoryTest(unittest.TestCase):
    """
    MemoryTest.
    """

    def test_make_ref(self):
        self.assertGreater(try_gc(), 0)
        obj = ExpensiveObject()
        ref_count = sys.getrefcount(obj)
        ref = make_ref(obj)
        self.assertEqual(sys.getrefcount(obj), ref_count)
        num_unreachable = try_gc()
        self.assertEqual(ref(), obj)
        del ref
        num_unreachable = try_gc()
        self.assertEqual(sys.getrefcount(obj), ref_count)
        del obj
        now_unreachable = try_gc()
        self.assertLessEqual(now_unreachable, num_unreachable)

    def test_make_proxy(self):
        self.assertGreater(try_gc(), 0)
        obj = ExpensiveObject()
        ref_count = sys.getrefcount(obj)
        proxy = make_proxy(obj)
        self.assertEqual(sys.getrefcount(obj), ref_count)
        num_unreachable = try_gc()
        self.assertEqual(proxy, obj)
        del proxy
        num_unreachable = try_gc()
        self.assertEqual(sys.getrefcount(obj), ref_count)
        del obj
        now_unreachable = try_gc()
        self.assertLessEqual(now_unreachable, num_unreachable)

    def test_try_gc(self):
        self.assertIsNotNone(try_gc())
