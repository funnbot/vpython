import itertools
from pathlib import Path

import numpy as np
from astropy.time import Time, TimeDelta
from vpython import acos, dot, vector
from vpython.no_notebook import stop_server
from vpython.rate_control import rate
from vpython.vpython import (
    arrow,
    attach_arrow,
    canvas,
    color,
    gcurve,
    graph,
    label,
    wtext,
)

import constants as const
from bodies import System
from linalg import axis_angle_between, axis_angle_to_euler, to_vpy_vec
from manuever import (
    apply_maneuver,
    calc_maneuver,
    parse_maneuvers,
    print_manuever_stats,
    save_manuevers,
)


class Simulation:
    system: System
    ttext: wtext
    g1: graph
    gc1: gcurve
    gc2: gcurve
    gc3: gcurve
    velocity_arrow: arrow

    delta_time: TimeDelta
    delta_time_sec: float
    length: int

    index: int
    sim_time: float
    current_time: Time

    def __init__(self):
        self.system = System(scale=const.SCALE, data_dir=Path("data"))

        self.sim_time = 0
        self.current_time = self.system.voyager2.ephemeris.start_time
        self.delta_time = self.system.voyager2.ephemeris.timestep
        self.delta_time_sec: float = float(self.delta_time.to_value(format="sec"))  # type: ignore
        self.ttext = wtext(text="")

        self.index = 0
        self.length = self.system.voyager2.ephemeris_len()

        self.g1 = graph(title="Timing")
        self.g1.follow_objects
        self.gc1 = gcurve(graph=self.g1, markers=True, color=color.red)
        self.gc2 = gcurve(graph=self.g1, color=color.blue)
        self.gc3 = gcurve(graph=self.g1, color=color.green)

        self.velocity_arrow = attach_arrow(
            self.system.voyager2,
            "velocity",
            color=vector(1, 0, 0),
            scale=const.SCALE * 500,
            headwidth=const.SCALE,
        )

    def reset(self):
        self.sim_time = 0
        self.current_time = self.system.voyager2.ephemeris.start_time
        self.index = 0
        for body in self.system.bodies:
            body.update_from_ephemeris(self.index)
    
    def update(self):
        pass
