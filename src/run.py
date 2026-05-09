import itertools
import signal
import sys
from pathlib import Path

import numpy as np
from astropy.time import TimeDelta
from vpython import acos, dot, vector
from vpython.no_notebook import signal_handler as vpy_signal_handler
from vpython.no_notebook import stop_server
from vpython.rate_control import rate
from vpython.vpython import attach_arrow, canvas, color, gcurve, graph, label, wtext

import constants as const
from bodies import System
from body import Body
from linalg import axis_angle_between, axis_angle_to_euler, to_vpy_vec
from manuever import (
    apply_maneuver,
    calc_maneuver,
    calc_percent_error,
    parse_maneuvers,
    print_manuever_stats,
    save_manuevers,
)


def exit():
    if STORE_MANUEVERS:
        save_manuevers()
    print_manuever_stats()


def signal_handler(sig, frame):
    exit()
    vpy_signal_handler(sig, frame)


signal.signal(signal.SIGINT, signal_handler)

STORE_MANUEVERS = False
APPLY_MANUEVERS = False

scale = 1000

scene = canvas(userspin=False, userzoom=True)
scene.range = 10000000

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
    scale=scale * 500,
    headwidth=scale,
)

index = 10700

for body in system.all_objects:
    body.update_from_ephemeris(index)


def update_model(dt: float):
    if index % 10 == 0:
        system.voyager2.update_closest_body(system.planets)

    closest_body: Body = system.voyager2.closest_body  # type: ignore

    system.voyager2.apply_gravity_force(closest_body)
    system.voyager2.apply_gravity_force(system.sun)
    closest_body.apply_gravity_force(system.sun)

    system.voyager2.integrate(dt)
    closest_body.integrate(dt)

    # for body in system.all_objects:
    #     body.apply_gravities(system.bodies)

    # for body in system.all_objects:
    #     body.integrate(dt)


sim_repeat = 100
sim_repeat_dt = delta_time_sec / sim_repeat


def update_sim():
    global index, delta_time_sec, sim_repeat, sim_repeat_dt, sim_repeat_range

    # setup simulation with accurate positions
    for body in system.bodies:
        body.update_from_ephemeris(index)

    if STORE_MANUEVERS:
        system.voyager2.update_from_ephemeris(index)
    else:
        # compare with real position
        system.voyager2_expected.update_from_ephemeris(index)

    # run simulation for this timestep, 90min
    for _ in range(sim_repeat):
        update_model(sim_repeat_dt)

    # just finished computing the next position, 90 mins later, so index+1 is the expected position
    # find the difference in simulated vs actual for next timestep
    if STORE_MANUEVERS:
        calc_maneuver(system.voyager2, index)
    elif APPLY_MANUEVERS:
        apply_maneuver(system.voyager2, index)

    gc1.plot(sim_time, calc_percent_error(system.voyager2, index))


def update():
    global current_time, sim_time, index

    update_sim()

    current_time += delta_time
    sim_time += delta_time_sec

    index += 1


if not STORE_MANUEVERS:
    parse_maneuvers()

# after jupiter: 11500
while index < 11500:
    rate(60)
    for _ in range(1):
        update()
    ttext.text = "{}, {}, {}, Closest: {}".format(
        current_time.to_datetime(),
        sim_time,
        index,
        system.voyager2.closest_body.name if system.voyager2.closest_body else "None",
    )
    # _body_stats(index, system.voyager2, gc1, gc2)

    scene.follow(system.voyager2)

exit()
