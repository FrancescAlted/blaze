import unittest
import sys
import blaze
import ctypes
import numpy as np
from blaze.ckernel import (CKernel, UnarySingleOperation,
        UnaryStridedOperation)

try:
    import dynd
    from dynd import nd, ndt, lowlevel
except ImportError:
    dynd = None

if sys.version_info >= (2, 7):
    from unittest import skipIf
else:
    from nose.plugins.skip import SkipTest
    class skipIf(object):
        def __init__(self, condition, reason):
            self.condition = condition
            self.reason = reason

        def __call__(self, func):
            if self.condition:
                from nose.plugins.skip import SkipTest
                def wrapped(*args, **kwargs):
                    raise SkipTest("Test %s is skipped because: %s" %
                                    (func.__name__, self.reason))
                wrapped.__name__ = func.__name__
                return wrapped
            else:
                return func

class TestDyNDCKernel(unittest.TestCase):
    @skipIf(dynd is None, 'dynd is not installed')
    def test_single_scalar_assign(self):
        # Make a CKernel that assigns one int64 to one float32
        ck = CKernel(UnarySingleOperation)
        lowlevel.py_api.make_assignment_kernel(
                        ndt.float32, ndt.int64, 'single',
                        ctypes.addressof(ck.dynamic_kernel_instance))
        # Do an assignment using ctypes
        i64 = ctypes.c_int64(1234)
        f32 = ctypes.c_float(1)
        ck(ctypes.addressof(f32), ctypes.addressof(i64))
        self.assertEqual(f32.value, 1234.0)

    @skipIf(dynd is None, 'dynd is not installed')
    def test_strided_scalar_assign(self):
        # Make a CKernel that assigns fixed-size strings to float32
        ck = CKernel(UnaryStridedOperation)
        lowlevel.py_api.make_assignment_kernel(
                        ndt.float32, nd.dtype('string(15,"A")'), 'strided',
                        ctypes.addressof(ck.dynamic_kernel_instance))
        # Do an assignment using a numpy array
        src = np.array(['3.25', '-1000', '1e5'], dtype='S15')
        dst = np.arange(3, dtype=np.float32)
        ck(dst.ctypes.data, 4, src.ctypes.data, 15, 3)
        self.assertEqual(dst.tolist(), [3.25, -1000, 1e5])

if __name__ == '__main__':
    unittest.main()
