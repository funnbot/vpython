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

open_ephemeris_csv("jwst_path_1day.csv")

# with open("jwst_path_1day.csv", "r", newline="", encoding="utf-8") as csvfile:
#     while True:
#         line = csvfile.readline()
#         if line.startswith("$$SOE"):
#             break
# reader = csv.reader(csvfile, delimiter=",")
# for row in reader:
#     time = Time(row[0], format="jd", scale="tdb")
#     pos = vector(float(row[2]), float(row[3]), float(row[4]))
#     vel = vector(float(row[5]), float(row[6]), float(row[7]))
#     ephemeris_point = EphemerisPoint(time=time, pos=pos, vel=vel)
#     ephemeris_points.append(ephemeris_point)

# scene = canvas()

# sun = sphere(pos=vector(0, 0, 0), radius=20, color=color.yellow)
# rocket = sphere(
#     pos=ephemeris_points[0].pos, radius=10, color=color.red, make_trail=True
# )

# index = 0

# while index < len(ephemeris_points):
#     rate(30)
#     rocket.pos = ephemeris_points[index].pos
#     index += 1
