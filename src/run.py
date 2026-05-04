import itertools
from pathlib import Path

import numpy as np
from vpython import dot, mag, vector
from vpython.rate_control import rate
from vpython.vpython import attach_arrow, canvas, color, gcurve, graph, label, wtext

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
delta_time_sec: float = float(delta_time.to_value(format="sec"))
ttext = wtext(text="")

index = 0
length = system.voyager2.ephemeris_len()
index_step = 2

g1 = graph(title="Timing")
gc1 = gcurve(graph=g1, color=color.red)
gc2 = gcurve(graph=g1, color=color.blue)

velocity_arrow = attach_arrow(
    system.voyager2, "velocity", color=vector(1, 0, 0), scale=scale
)

index = 1000

for body in system.bodies:
    body.update_from_ephemeris(index)


def update_model(dt: float):
    for body1, body2 in system_pairs:
        body1.apply_force(body1.grav_force_on_self_by(body2))
        body2.apply_force(body2.grav_force_on_self_by(body1))

    for body in system.bodies:
        body.integrate(dt)


def update():
    # global index, current_time
    repeat = 200
    dt = (delta_time_sec * index_step) / repeat
    for _ in range(repeat):
        update_model(dt)
    
    # update_model(delta_time_sec * index_step)
    # system.voyager2_real.update_from_ephemeris(index)


def _percent_diff(model: float, expected: float) -> float:
    if expected == 0:
        return float("inf") if model != 0 else 0
    return abs(model - expected) / abs(expected) * 100

# (magnitude, angle)
def _vec_diff(model: vector, expected: vector) -> tuple[float, float]:
    model_mag = model.mag
    expected_mag = expected.mag
    mag_diff = _percent_diff(model_mag, expected_mag)
    angle_diff = 0
    if model_mag == 0 or expected_mag == 0:
        angle_diff = float("inf") if model_mag != expected_mag else 0
    else:
        angle_diff = np.arccos(dot(model, expected) / (model_mag * expected_mag))
    return mag_diff, angle_diff


def _body_stats(index: int, body, gmag: gcurve, gangle: gcurve):
    expected_vel = to_vpy_vec(body.ephemeris.velocities[index])
    mag_diff, angle_diff = _vec_diff(body.velocity, expected_vel)
    gmag.plot(sim_time, mag_diff)
    gangle.plot(sim_time, angle_diff)


while index < length:
    rate(1000)
    update()
    ttext.text = "{}".format(current_time.to_datetime())

    current_time += delta_time * index_step
    sim_time += delta_time_sec * index_step



    _body_stats(index, system.voyager2, gc1, gc2)

    index += index_step
    scene.follow(system.sun)
