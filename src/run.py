import itertools
from pathlib import Path

import numpy as np
from astropy.time import TimeDelta
from vpython import dot, mag, vector, acos
from vpython.rate_control import rate
from vpython.vpython import attach_arrow, canvas, color, gcurve, graph, label, wtext

import constants as const
from bodies import System
from body import Body
from linalg import to_vpy_vec

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
gc1 = gcurve(graph=g1, color=color.red)
gc2 = gcurve(graph=g1, color=color.blue)
gc3 = gcurve(graph=g1, color=color.green)

velocity_arrow = attach_arrow(
    system.voyager2, "velocity", color=vector(1, 0, 0), scale=scale * 100
)

index = 10100

for body in system.bodies:
    body.update_from_ephemeris(index)


def _percent_diff(model: float, expected: float) -> float:
    if expected == 0:
        return float("inf") if model != 0 else 0
    return abs(model - expected) / abs(expected) * 100


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


def _angle_between(vec1: vector, vec2: vector) -> float:
    mag1 = mag(vec1)
    mag2 = mag(vec2)
    if mag1 == 0 or mag2 == 0:
        return float("inf") if mag1 != mag2 else 0
    return acos(np.clip(dot(vec1, vec2) / (mag1 * mag2), -1, 1))


delta_v_array: list[tuple[float, float, float, vector]] = []


def _body_stats(index: int, body, gmag: gcurve, gangle: gcurve):
    expected_vel = to_vpy_vec(body.ephemeris.velocities[index])
    mag_diff, angle_diff = _vec_diff(body.velocity, expected_vel)
    gmag.plot(sim_time, mag_diff)
    gangle.plot(sim_time, angle_diff)


def _calc_maneuver(body: Body):
    expected_vel = to_vpy_vec(body.ephemeris.velocities[index])
    vel_mag = body.velocity.mag
    expected_mag = expected_vel.mag
    delta_v: vector = expected_vel - body.velocity

    mag_diff = expected_mag - vel_mag
    angle_diff = _angle_between(body.velocity, expected_vel) * (180 / np.pi)

    percent_diff = (
        (abs(mag_diff) / expected_mag) + (abs(angle_diff) / 360)
    ) * 100
    gc1.plot(sim_time, percent_diff)
    if percent_diff < 0.01:
        mag_diff = 0
        angle_diff = 0
    delta_v_array.append(((sim_time) / (60**2 * 24), mag_diff, angle_diff, delta_v))

    # gc1.plot(sim_time, mag_diff)
    # gc2.plot(sim_time, angle_diff)
    # gc3.plot(sim_time, delta_v.z)

    body.update_from_ephemeris(index + 1)


def update_model(dt: float):
    for body in system.bodies:
        body.apply_gravities(system.bodies)

    for body in system.bodies:
        body.integrate(dt)


def update_sim():
    global index, delta_time_sec
    repeat = 20
    dt = delta_time_sec / repeat
    for _ in range(repeat):
        update_model(dt)

    for body in system.planets:
        body.update_from_ephemeris(index + 1)

    # if index % 1000 == 0:
    #     system.voyager2.update_from_ephemeris(index + 1)


def update():
    global current_time, sim_time, index

    update_sim()

    _calc_maneuver(system.voyager2)

    current_time += delta_time
    sim_time += delta_time_sec

    index += 1


def save_delta_v():
    with open("delta_v.csv", "w") as f:
        f.write("days, mag_diff, angle_diff, delta_v\n")
        for i in range(len(delta_v_array)):
            delta_v = delta_v_array[i]
            f.write(
                f"{delta_v[0]:<10} days,{delta_v[1]:<25},{delta_v[2]:<25},{delta_v[3]}\n"
            )


while index < 15000:
    rate(1000)
    for _ in range(50):
        update()
    ttext.text = "{}, {}, {}".format(current_time.to_datetime(), sim_time, index)
    # _body_stats(index, system.voyager2, gc1, gc2)

    scene.follow(system.voyager2)

sum_diff_mag = sum(diff[1] for diff in delta_v_array)
sum_diff_angle = sum(diff[2] for diff in delta_v_array)
print(f"Total delta-v magnitude difference: {sum_diff_mag:.2f}")
print(f"Total delta-v angle difference: {sum_diff_angle:.2f}")

save_delta_v()
