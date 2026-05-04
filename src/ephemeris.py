"""Parsing ephemeris data from https://ssd.jpl.nasa.gov/horizons/app.html"""

import csv
import itertools
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import numpy as np
from astropy.time import Time, TimeDelta

from linalg import RowVec3dArray, Vec3d

CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(exist_ok=True)


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


def _to_cache_path(file_path: Path) -> Path:
    return (CACHE_DIR / file_path.name).with_suffix(".npz")


def _time_to_np(time: Time | TimeDelta) -> np.ndarray:
    vals = time.to_value("jd", subfmt="bytes")
    return vals  # type: ignore


def _time_from_np(arr: np.ndarray) -> Time:
    return Time(arr, format="jd", scale="tdb", in_subfmt="bytes")


def _time_delta_from_np(arr: np.ndarray) -> TimeDelta:
    return TimeDelta(arr, format="jd", scale="tdb", in_subfmt="bytes")


def load_cache(file_path: Path) -> Ephemeris | None:
    cache_path = _to_cache_path(file_path)
    if not cache_path.exists():
        return None
    if not cache_path.is_file():
        return None
    if not cache_path.stat().st_size > 0:
        return None
    with np.load(cache_path) as cache:
        return Ephemeris(
            positions=cache["positions"],
            velocities=cache["velocities"],
            start_time=_time_from_np(cache["start_time"]),
            timestep=_time_delta_from_np(cache["timestep"]),
        )


def save_cache(file_path: Path, ephemeris: Ephemeris):
    cache_path = _to_cache_path(file_path)
    if cache_path.exists():
        return

    with open(cache_path, "wb") as f:
        np.savez(
            f,
            positions=ephemeris.positions,
            velocities=ephemeris.velocities,
            start_time=_time_to_np(ephemeris.start_time),
            timestep=_time_to_np(ephemeris.timestep),
        )


# JDTDB, Calendar Date (TDB), X, Y, Z, VX, VY, VZ
def parse_ephemeris_from_csv(file_path: Path, use_cache: bool = True) -> Ephemeris:
    if use_cache:
        cached_ephemeris = load_cache(file_path)
        if cached_ephemeris is not None:
            return cached_ephemeris

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

    ephemeris = Ephemeris(
        positions=np.array(positions),
        velocities=np.array(velocities),
        start_time=times[0],
        timestep=times[1] - times[0],
    )

    if use_cache:
        save_cache(file_path, ephemeris)

    return ephemeris
