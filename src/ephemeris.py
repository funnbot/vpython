"""Parsing ephemeris data from https://ssd.jpl.nasa.gov/horizons/app.html"""

import csv
import itertools
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, Iterator, Literal

import numpy as np
from astropy.time import Time, TimeDelta
from numpy.typing import NDArray

from linalg import RowVec3dArray, Vec3d


@dataclass(frozen=True)
class EphemerisPoint:
    time: Time
    pos: Vec3d
    vel: Vec3d


@dataclass(frozen=True)
class Ephemeris:
    positions: RowVec3dArray
    velocities: RowVec3dArray
    start_time: Time
    timestep: TimeDelta


def _parse_row(row: list[str]) -> EphemerisPoint:
    try:
        return EphemerisPoint(
            time=Time(row[0], format="jd", scale="tdb"),
            pos=np.array([float(row[2]), float(row[3]), float(row[4])]),
            vel=np.array([float(row[5]), float(row[6]), float(row[7])]),
        )
    except Exception as e:
        raise ValueError(f"Error parsing row: {row}") from e


# JDTDB, Calendar Date (TDB), X, Y, Z, VX, VY, VZ
def parse_ephemeris_from_csv(file_path: Path) -> Ephemeris:
    positions: list[Vec3d] = []
    velocities: list[Vec3d] = []
    times: list[Time] = []
    with open(file_path, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        reader = itertools.dropwhile(
            # line could be empty
            lambda line: len(line) == 0 or not line[0].startswith("$$SOE"),
            reader,
        )
        next(reader)  # skip the $$SOE line

        for row in reader:
            if row[0].startswith("$$EOE"):
                break
            point = _parse_row(row)
            positions.append(point.pos)
            velocities.append(point.vel)
            times.append(point.time)
    return Ephemeris(
        positions=np.array(positions),
        velocities=np.array(velocities),
        start_time=times[0],
        timestep=times[1] - times[0],
    )
