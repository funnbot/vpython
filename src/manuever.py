import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from vpython import vector

import constants as const
from body import Body
from linalg import (
    axis_angle_between,
    percent_vec_uncertainty,
    percent_vec_uncertainty_sum,
    to_vpy_vec,
)


@dataclass(frozen=True)
class Maneuver:
    index: int
    magnitude: float
    rot_axis: vector
    rot_angle: float
    percent_error: float
    delta_v: vector


manuever_dict: dict[int, Maneuver] = {}
manuever_list: list[Maneuver] = []
total_percent_error = 0
percent_error_count = 0


def _percent_diff(diff: float, range: float) -> float:
    if range == 0:
        return float("inf") if diff != 0 else 0
    return abs(diff) / range * 100


def apply_maneuver(body: Body, index: int):
    if index not in manuever_dict:
        return
    m = manuever_dict[index]
    print(
        f"Applying maneuver at index {index}, mag: {m.magnitude:.2f}, angle: {m.rot_angle:.2f}, percent error: {m.percent_error:.2f}%"
    )

    body.velocity += m.delta_v

    # # rotate current velocity by the maneuver's rotation
    # new_velocity = body.velocity.rotate(angle=m.rot_angle, axis=m.rot_axis)
    # # then add the magnitude change in the direction of the new velocity
    # if new_velocity.mag != 0:
    #     new_velocity = new_velocity.norm() * m.magnitude + new_velocity
    # else:
    #     new_velocity = vector(m.magnitude, 0, 0)  # arbitrary direction if no velocity
    # body.velocity = new_velocity


def parse_maneuvers():
    if not Path("manuevers.csv").exists():
        return
    with open("manuevers.csv", "r", newline="") as f:
        next(f)  # skip header
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if len(row) != 10:
                continue
            index = int(row[0])
            manuever = Maneuver(
                index,
                magnitude=float(row[1]),
                rot_axis=vector(float(row[2]), float(row[3]), float(row[4])),
                rot_angle=float(row[5]),
                percent_error=float(row[6]),
                delta_v=vector(float(row[7]), float(row[8]), float(row[9])),
            )
            manuever_dict[index] = manuever


def _chi_squared(value: float, expected: float, uncertainty: float) -> float:
    assert uncertainty > 0, "Uncertainty must be greater than zero"
    return ((value - expected) / uncertainty) ** 2


def _vec_chi_squared(value: vector, expected: vector, uncertainty: float) -> float:
    return (
        _chi_squared(value.x, expected.x, uncertainty)
        + _chi_squared(value.y, expected.y, uncertainty)
        + _chi_squared(value.z, expected.z, uncertainty)
    )


def calc_percent_error(body: Body, index: int) -> float:
    global total_percent_error, percent_error_count
    expected_vec = to_vpy_vec(body.ephemeris.velocities[index + 1])

    value = percent_vec_uncertainty_sum(body.velocity, expected_vec)
    total_percent_error += value
    percent_error_count += 1

    return value


def calc_maneuver(body: Body, index: int):
    expected_vel = to_vpy_vec(body.ephemeris.velocities[index + 1])
    delta_v = expected_vel - body.velocity

    mag_diff = expected_vel.mag - body.velocity.mag
    # resulting angle if applied should rotate the current velocity to the expected velocity
    angle_axis, angle_diff = axis_angle_between(body.velocity, expected_vel)

    diff_percent = percent_vec_uncertainty_sum(body.velocity, expected_vel)

    if diff_percent < 0.01:
        return

    manuever = Maneuver(
        index,
        mag_diff,
        angle_axis,
        angle_diff,
        diff_percent,
        delta_v,
    )

    manuever_list.append(manuever)


saved_maneuvers = False


def save_manuevers():
    global saved_maneuvers
    if len(manuever_list) == 0 or saved_maneuvers:
        return
    with open("manuevers.csv", "w") as f:
        f.write(
            "index, mag, rot_axis_x, rot_axis_y, rot_axis_z, rot_angle, diff_percent, delta_v_x, delta_v_y, delta_v_z\n"
        )
        for m in manuever_list:
            f.write(
                f"{m.index},{m.magnitude:.8f},{m.rot_axis.x:.8f},{m.rot_axis.y:.8f},{m.rot_axis.z:.8f},{m.rot_angle:.8f},{m.percent_error:.2f},{m.delta_v.x:.8f},{m.delta_v.y:.8f},{m.delta_v.z:.8f}\n"
            )
    saved_maneuvers = True


def _get_maneuvers() -> list[Maneuver]:
    if len(manuever_list) > 0:
        return manuever_list
    return list(manuever_dict.values())


def print_manuever_stats():
    manuevers = _get_maneuvers()

    print(f"Calculated {len(manuevers)} manuevers:")
    sum_diff_mag = sum(m.magnitude for m in manuevers)
    sum_diff_angle = sum(m.rot_angle for m in manuevers)
    total_error_percent = sum(m.percent_error for m in manuevers)
    percent_error = (
        total_percent_error / percent_error_count if percent_error_count > 0 else 0
    )
    print(f"Manuever delta-v magnitude difference: {sum_diff_mag:.4f}")
    print(f"Manuever delta-v angle difference: {sum_diff_angle:.4f}")
    print(f"Manuever percent error: {total_error_percent:.4f}%")
    print(f"Total velocity percent error: {percent_error:.6f}")
