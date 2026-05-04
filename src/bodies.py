from pathlib import Path

from vpython.vpython import color

import constants as const
from body import Body
from ephemeris import parse_ephemeris_from_csv


class System:
    def __init__(self, scale: float, data_dir: Path):
        self.sun = Body(
            ephemeris=parse_ephemeris_from_csv(data_dir / "sun_ephemeris.txt"),
            mass=const.MASS_SUN,
            physical_radius=const.RADIUS_SUN,
            scale=10,
            color=color.yellow,
            make_trail=False,
        )

        self.earth = Body(
            ephemeris=parse_ephemeris_from_csv(data_dir / "earth_ephemeris.txt"),
            mass=const.MASS_EARTH,
            physical_radius=const.RADIUS_EARTH,
            scale=scale,
            color=color.blue,
            make_trail=True,
            retain=1000,
        )

        self.moon = Body(
            ephemeris=parse_ephemeris_from_csv(data_dir / "moon_ephemeris.txt"),
            mass=const.MASS_MOON,
            physical_radius=const.RADIUS_MOON,
            scale=scale,
            color=color.white,
            make_trail=True,
            retain=300,
        )

        self.neptune = Body(
            ephemeris=parse_ephemeris_from_csv(data_dir / "neptune_ephemeris.txt"),
            mass=const.MASS_NEPTUNE,
            physical_radius=const.RADIUS_NEPTUNE,
            scale=scale,
            color=color.cyan,
            make_trail=True,
            # retain=300,
        )

        self.saturn = Body(
            ephemeris=parse_ephemeris_from_csv(data_dir / "saturn_ephemeris.txt"),
            mass=const.MASS_SATURN,
            physical_radius=const.RADIUS_SATURN,
            scale=scale,
            color=color.orange,
            make_trail=True,
            # retain=300,
        )

        self.jupiter = Body(
            ephemeris=parse_ephemeris_from_csv(data_dir / "jupiter_bc_ephemeris.txt"),
            mass=const.MASS_JUPITER,
            physical_radius=const.RADIUS_JUPITER,
            scale=scale,
            color=color.magenta,
            make_trail=True,
            # retain=300,
        )

        self.uranus = Body(
            ephemeris=parse_ephemeris_from_csv(data_dir / "uranus_ephemeris.txt"),
            mass=const.MASS_URANUS,
            physical_radius=const.RADIUS_URANUS,
            scale=scale,
            color=color.green,
            make_trail=True,
            # retain=300,
        )

        self.voyager2 = Body(
            ephemeris=parse_ephemeris_from_csv(data_dir / "voyager2_ephemeris.txt"),
            mass=const.MASS_VOYAGER2,
            physical_radius=1000,
            scale=scale,
            color=color.red,
            make_trail=True,
        )

        self.bodies = [
            self.sun,
            self.earth,
            self.moon,
            self.voyager2,
            self.neptune,
            self.saturn,
            self.jupiter,
            self.uranus,
        ]
