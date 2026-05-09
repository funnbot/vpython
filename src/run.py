import csv
import itertools
from pathlib import Path

import numpy as np
from astropy.time import TimeDelta
from vpython import acos, dot, vector
from vpython.no_notebook import stop_server
from vpython.rate_control import rate
from vpython.vpython import attach_arrow, canvas, color, gcurve, graph, label, wtext

import constants as const
from bodies import System
from body import Body
from linalg import axis_angle_between, axis_angle_to_euler, to_vpy_vec

scale = 1000

scene = canvas(userspin=False, userzoom=True)

system = System(scale=scale, data_dir=Path("data"))
system_pairs = list(itertools.combinations(system.bodies, 2))

sim_time = 0
current_time = system.voyager2.ephemeris.start_time
delta_time = system.voyager2.ephemeris.timestep
delta_time_sec: float = float(delta_time.to_value(format="sec"))  # type: ignore
ttext = wtext(text="")

index = 0
length = system.voyager2.ephemeris_len()

g1 = graph(title="Timing")
g1.follow_objects
gc1 = gcurve(graph=g1, markers=True, color=color.red)
gc2 = gcurve(graph=g1, color=color.blue)
gc3 = gcurve(graph=g1, color=color.green)

velocity_arrow = attach_arrow(
    system.voyager2,
    "velocity",
    color=vector(1, 0, 0),
    scale=scale * 1000,
    headwidth=scale,
)

index = 10700

for body in system.bodies:
    body.update_from_ephemeris(index)


def _percent_diff(diff: float, range: float) -> float:
    if range == 0:
        return float("inf") if diff != 0 else 0
    return abs(diff) / range * 100


# (magnitude, angle)
def _vec_diff(model: vector, expected: vector) -> tuple[float, float]:
    model_mag = model.mag
    expected_mag = expected.mag
    diff = model - expected
    mag_diff = diff.mag / expected_mag * 100

    angle_diff = 0
    if model_mag == 0 or expected_mag == 0:
        angle_diff = float("inf") if model_mag != expected_mag else 0
    else:
        angle_diff = acos(
            np.clip(dot(model, expected) / (model_mag * expected_mag), -1, 1)
        )
        angle_diff = (
            angle_diff / (2 * np.pi) * 100
        )  # convert to percentage of full circle
    return mag_diff, angle_diff


delta_v_array: list[tuple[float, float, float, float, float]] = []


class Maneuver:
    index: int
    magnitude: float
    rot_axis: vector
    rot_angle: float
    percent_error: float

    def __init__(
        self,
        index: int,
        magnitude: float,
        rot_axis: vector,
        rot_angle: float,
        percent_error: float,
    ):
        self.index = index
        self.magnitude = magnitude
        self.rot_axis = rot_axis
        self.rot_angle = rot_angle
        self.percent_error = percent_error


manuever_list: list[Maneuver] = []
manuever_dict: dict[int, Maneuver] = {}


def _body_stats(index: int, body, gpos: gcurve, gmag: gcurve, gangle: gcurve):
    expected_vel = to_vpy_vec(body.ephemeris.velocities[index + 1])
    expected_mag = expected_vel.mag

    mag_diff = expected_vel.mag - body.velocity.mag
    # resulting angle if applied should rotate the current velocity to the expected velocity
    angle_axis, angle_diff = axis_angle_between(body.velocity, expected_vel)

    mag_diff = _percent_diff(mag_diff, expected_mag)
    angle_diff = _percent_diff(np.rad2deg(angle_diff), 360)

    expected_pos = to_vpy_vec(body.ephemeris.positions[index + 1])
    pos_diff = (body.pos - expected_pos).mag
    gpos.plot(sim_time, pos_diff)

    gmag.plot(sim_time, mag_diff)
    gangle.plot(sim_time, angle_diff)


def _parse_maneuvers():
    with open("manuevers.csv", "r", newline="") as f:
        next(f)  # skip header
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if len(row) != 7:
                continue
            index = int(row[0])
            magnitude = float(row[1])
            rot_axis = vector(float(row[2]), float(row[3]), float(row[4]))
            rot_angle = float(row[5])
            percent_error = float(row[6])
            manuever_list.append(
                Maneuver(index, magnitude, rot_axis, rot_angle, percent_error)
            )
            manuever_dict[index] = manuever_list[-1]


_parse_maneuvers()


def _apply_maneuver(body: Body, index: int):
    if index not in manuever_dict:
        return
    m = manuever_dict[index]
    print(f"Applying maneuver at index {index}, mag: {m.magnitude:.2f}, angle: {m.rot_angle:.2f}, percent error: {m.percent_error:.2f}%")
    # rotate current velocity by the maneuver's rotation
    new_velocity = body.velocity.rotate(angle=m.rot_angle, axis=m.rot_axis)
    # then add the magnitude change in the direction of the new velocity
    if new_velocity.mag != 0:
        new_velocity = new_velocity.norm() * m.magnitude + new_velocity
    else:
        new_velocity = vector(m.magnitude, 0, 0)  # arbitrary direction if no velocity
    body.velocity = new_velocity


def _calc_maneuver(body: Body):
    expected_vel = to_vpy_vec(body.ephemeris.velocities[index + 1])
    expected_mag = expected_vel.mag

    mag_diff = expected_vel.mag - body.velocity.mag
    # resulting angle if applied should rotate the current velocity to the expected velocity
    angle_axis, angle_diff = axis_angle_between(body.velocity, expected_vel)

    diff_percent = _percent_diff(mag_diff, expected_mag) + _percent_diff(
        np.rad2deg(angle_diff), 360
    )
    gc1.plot(index, diff_percent)
    if diff_percent < 0.01:
        return

    manuever_list.append(
        Maneuver(
            index,
            mag_diff,
            angle_axis,
            angle_diff,
            diff_percent,
        )
    )

    # delta_v_array.append(
    #     (
    #         (sim_time) / (60**2 * 24),
    #         mag_diff,
    #         angle_diff,
    #         diff_percent,
    #     )
    # )

    # gc1.plot(sim_time, mag_diff)
    # gc2.plot(sim_time, angle_diff)
    # gc3.plot(sim_time, delta_v.z)


def update_model(dt: float):
    for body in system.bodies:
        body.apply_gravities(system.bodies)

    for body in system.bodies:
        body.integrate(dt)


def update_sim():
    global index, delta_time_sec

    # setup simulation with accurate positions
    for body in system.planets:
        body.update_from_ephemeris(index)
    system.voyager2.update_from_ephemeris(index)

    # run simulation for this timestep, 90min
    repeat = 50
    dt = delta_time_sec / repeat
    for _ in range(repeat):
        update_model(dt)

    # just finished computing the next position, 90 mins later, so index+1 is the expected position
    # find the difference in simulated vs actual for next timestep
    #_calc_maneuver(system.voyager2)
    _apply_maneuver(system.voyager2, index)
    _body_stats(index, system.voyager2, gc1, gc2, gc3)

    # if index % 1000 == 0:
    #     system.voyager2.update_from_ephemeris(index + 1)


def update():
    global current_time, sim_time, index

    update_sim()

    current_time += delta_time
    sim_time += delta_time_sec

    index += 1


def save_manuevers():
    if len(manuever_list) == 0:
        return
    with open("manuevers.csv", "w") as f:
        f.write(
            "index, mag, rot_axis_x, rot_axis_y, rot_axis_z, rot_angle, diff_percent\n"
        )
        for m in manuever_list:
            f.write(
                f"{m.index},{m.magnitude:.6f},{m.rot_axis.x:.6f},{m.rot_axis.y:.6f},{m.rot_axis.z:.6f},{m.rot_angle:.6f},{m.percent_error:.2f}\n"
            )

# after jupiter: 11500
while index < 11500:
    rate(1000)
    for _ in range(10):
        update()
    ttext.text = "{}, {}, {}".format(current_time.to_datetime(), sim_time, index)
    # _body_stats(index, system.voyager2, gc1, gc2)

    scene.follow(system.voyager2)

sum_diff_mag = sum(m.magnitude for m in manuever_list)
sum_diff_angle = sum(m.rot_angle for m in manuever_list)
print(f"Total delta-v magnitude difference: {sum_diff_mag:.2f}")
print(f"Total delta-v angle difference: {sum_diff_angle:.2f}")

save_manuevers()
