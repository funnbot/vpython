import numpy as np
from typing import Iterable, Literal as L

from vpython import vector

# numpy data is row major
# [1, 2, 3] is neither, but tends to be treated as a row vector `(3, 1)`
# a row vector is of shape (3,) and a column vector is of shape (3, 1)
# a matrix is of shape (m, n) where m is the number of rows and n is the number of columns

type Vec3d = np.ndarray[tuple[L[3]], np.dtype[np.float64]]
"""vector of shape (3,) """

type RowVec3d = np.ndarray[tuple[L[1], L[3]], np.dtype[np.float64]]
"""row vector of shape (1, 3) """

type ColVec3d = np.ndarray[tuple[L[3], L[1]], np.dtype[np.float64]]
"""column vector of shape (3, 1) """

type RowVec3dArray = np.ndarray[tuple[int, L[3]], np.dtype[np.float64]]
"""array of row vectors, shape (n, 3)"""

type ColVec3dArray = np.ndarray[tuple[L[3], int], np.dtype[np.float64]]
"""array of column vectors, shape (3, n)"""


def reshape_to_row_vec(vec: Vec3d | ColVec3d) -> RowVec3d:
    """Convert a vector to a row vector (shape (1, 3))"""
    return vec.reshape((1, 3))  # type: ignore


def reshape_to_col_vec(vec: Vec3d | RowVec3d) -> ColVec3d:
    """Convert a vector to a column vector (shape (3, 1))"""
    return vec.reshape((3, 1))  # type: ignore


def reshape_to_vec3d(vec: RowVec3d | ColVec3d) -> Vec3d:
    """Convert a row or column vector to a vector (shape (3,))"""
    return vec.reshape((3,))  # type: ignore


def make_vec3d_array(vecs: Iterable[Vec3d]) -> RowVec3dArray:
    """Convert an iterable of vectors to an array of row vectors (shape (n, 3))"""
    return np.array(vecs, dtype=np.float64).reshape((-1, 3))  # type: ignore


def reshape_to_col_vec_array(vecs: Iterable[Vec3d]) -> ColVec3dArray:
    """Convert an iterable of vectors to an array of column vectors (shape (3, n))"""
    return np.array(vecs, dtype=np.float64).reshape((3, -1))  # type: ignore


def to_vpy_vec(vec: Vec3d) -> vector:
    """Convert a Vec3d to a vpython vector"""
    return vector(vec[0], vec[1], vec[2])
