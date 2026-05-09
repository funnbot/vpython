from typing import Iterable
from typing import Literal as L

import numpy as np
from vpython import acos, dot, mag, vector

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


def set_vpy_vec(vpy_vec: vector, new_vec: Vec3d):
    """Set the components of a vpython vector to the values of a Vec3d"""
    vpy_vec.x = new_vec[0]
    vpy_vec.y = new_vec[1]
    vpy_vec.z = new_vec[2]


def angle_between(vec1: vector, vec2: vector) -> float:
    mag1 = mag(vec1)
    mag2 = mag(vec2)
    if mag1 == 0 or mag2 == 0:
        return float("inf") if mag1 != mag2 else 0
    return acos(np.clip(dot(vec1, vec2) / (mag1 * mag2), -1, 1))


def axis_angle_between(vec1: vector, vec2: vector) -> tuple[vector, float]:
    mag1 = mag(vec1)
    mag2 = mag(vec2)
    if mag1 == 0 or mag2 == 0:
        return vector(0, 0, 0), float("inf") if mag1 != mag2 else 0
    angle = acos(np.clip(dot(vec1, vec2) / (mag1 * mag2), -1, 1))
    axis = vec1.cross(vec2).hat
    return axis, angle


def axis_angle_to_euler(axis: vector, angle: float) -> vector:
    s = np.sin(angle)
    c = np.cos(angle)
    t = 1 - c

    pole = axis.x * axis.y * t + axis.z * s
    if pole > 0.998:  # north pole singularity
        heading = 2 * np.arctan2(axis.x * np.sin(angle / 2), np.cos(angle / 2))
        attitude = np.pi / 2
        bank = 0
        return vector(heading, attitude, bank)
    elif pole < -0.998:  # south pole singularity
        heading = -2 * np.arctan2(axis.x * np.sin(angle / 2), np.cos(angle / 2))
        attitude = -np.pi / 2
        bank = 0
        return vector(heading, attitude, bank)

    heading = np.arctan2(
        axis.y * s - axis.x * axis.z * t, 1 - (axis.y * axis.y + axis.z * axis.z) * t
    )
    attitude = np.arcsin(pole)
    bank = np.arctan2(
        axis.x * s - axis.y * axis.z * t, 1 - (axis.x * axis.x + axis.z * axis.z) * t
    )
    return vector(heading, attitude, bank)
