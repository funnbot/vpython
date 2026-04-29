from vpython import vector
from vpython.vpython import canvas, sphere, color
from vpython.rate_control import rate

import numpy as np
from numpy.typing import NDArray
from astropy.time import Time

import itertools
from typing import Literal, Iterable
import csv
from datetime import datetime, timedelta
from dataclasses import dataclass

type Vec3d = np.ndarray[tuple[Literal[3]], np.dtype[np.float64]]
type Vec3dArray = np.ndarray[tuple[Literal[3]], np.dtype[np.float64]]

START_DATE = datetime(2021, 12, 25, 13, 0, 9, 1840)


@dataclass(frozen=True)
class EphemerisPoint:
    time: Time
    pos: vector
    vel: vector


class Ephemeris:
    positions: Vec3dArray
    velocities: Vec3dArray
    times: list[Time]


ephemeris_points = []


# JDTDB, Calendar Date (TDB), X, Y, Z, VX, VY, VZ
def open_ephemeris_csv(file_path: str):
    positions: list[Vec3d] = []
    velocities: list[Vec3d] = []
    times: list[Time] = []
    with open("jwst_path_1day.csv", "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        reader = itertools.dropwhile(
            lambda line: not line[0].startswith("$$SOE"), reader
        )
        next(reader)  # skip the $$SOE line
        header = list(map(lambda s: s.strip(), next(reader)))
        assert header[0:8] == [
            "JDTDB",
            "Calendar Date (TDB)",
            "X",
            "Y",
            "Z",
            "VX",
            "VY",
            "VZ",
        ], f"Unexpected header: {header}"
        # start = itertools.dropwhile(lambda line: not line.startswith("$$SOE"), csvfile)
        # next(start)  # skip the $$SOE line
        # remove_end = itertools.takewhile(
        #     lambda line: not line.startswith("$$EOE"), start
        # )

        # reader = csv.reader(remove_end, delimiter=",")
        # return map(
        #     lambda row: EphemerisPoint(
        #         time=Time(row[0], format="jd", scale="tdb"),
        #         pos=vector(float(row[2]), float(row[3]), float(row[4])),
        #         vel=vector(float(row[5]), float(row[6]), float(row[7])),
        #     ),
        #     reader,
        # )
