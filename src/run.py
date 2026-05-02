import csv
import itertools
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, Literal

import numpy as np
from astropy.time import Time
from numpy.typing import NDArray
from vpython import mag, vector
from vpython.rate_control import rate
from vpython.vpython import arrow, attach_arrow, canvas, color, label, sphere, text

import constants as const
from bodies import System
from body import Body
from ephemeris import parse_ephemeris_from_csv
from linalg import to_vpy_vec

scale = 1000

scene = canvas(userspin=False, userzoom=True)

system = System(scale=scale, data_dir=Path("data"))

time = system.voyager2.ephemeris.start_time
deltaTime = system.voyager2.ephemeris.timestep
tstr = "Time: {:.0f} days".format(0)
tlabel = label(pos=vector(0, 0, 0), text=tstr)

index = 0

while index < system.voyager2.ephemeris_len():
    rate(500)

    for body in system.bodies:
        body.update_from_ephemeris(index)

    tstr = "Time: {} days".format(time.to_datetime())
    tlabel.text = tstr

    time += deltaTime
    index += 2
    scene.follow(system.sun)
