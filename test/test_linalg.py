import unittest

import numpy as np
import numpy.testing as npt

from src.linalg import (
    make_vec3d_array,
    reshape_to_col_vec,
    reshape_to_row_vec,
    reshape_to_vec3d,
)


class TestLinalg(unittest.TestCase):
    def test_reshape_to_row_vec(self):
        vec = np.array([1.0, 2.0, 3.0])
        row_vec = reshape_to_row_vec(vec)
        self.assertEqual(row_vec.shape, (1, 3))
        npt.assert_array_equal(row_vec, [[1.0, 2.0, 3.0]])

        col_vec = reshape_to_col_vec(vec)
        self.assertEqual(col_vec.shape, (3, 1))
        npt.assert_array_equal(col_vec, [[1.0], [2.0], [3.0]])

    def test_reshape_to_col_vec(self):
        vec = np.array([1.0, 2.0, 3.0])
        col_vec = reshape_to_col_vec(vec)
        self.assertEqual(col_vec.shape, (3, 1))
        np.testing.assert_array_equal(col_vec, [[1.0], [2.0], [3.0]])

    def test_reshape_to_vec3d(self):
        row_vec = np.array([[1.0, 2.0, 3.0]])
        vec = reshape_to_vec3d(row_vec)
        self.assertEqual(vec.shape, (3,))
        npt.assert_array_equal(vec, [1.0, 2.0, 3.0])

        col_vec = np.array([[1.0], [2.0], [3.0]])
        vec = reshape_to_vec3d(col_vec)
        self.assertEqual(vec.shape, (3,))
        npt.assert_array_equal(vec, [1.0, 2.0, 3.0])

    def test_make_vec3d_array(self):
        vecs = [np.array([1.0, 2.0, 3.0]), np.array([4.0, 5.0, 6.0])]
        array = make_vec3d_array(vecs)
        self.assertEqual(array.shape, (2, 3))
        npt.assert_array_equal(array, [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])


if __name__ == "__main__":
    unittest.main()
