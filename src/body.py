# why pylance angry?
from astropy.constants import G  # type: ignore
from vpython import mag, vector
from vpython.vpython import sphere

from ephemeris import Ephemeris
from linalg import to_vpy_vec

G_val = float(G.to("km3 / (kg s2)").value)


class Body(sphere):
    velocity: vector
    acceleration: vector
    mass: float
    physical_radius: float
    ephemeris: Ephemeris

    def __init__(
        self,
        ephemeris: Ephemeris,
        mass: float,
        physical_radius: float,
        scale: float,
        **kwargs,
    ):
        initial_pos = to_vpy_vec(ephemeris.positions[0])
        kwargs["pos"] = initial_pos
        kwargs["radius"] = physical_radius * scale
        super().__init__(**kwargs)

        self.velocity = to_vpy_vec(ephemeris.velocities[0])
        self.acceleration = vector(0, 0, 0)
        self.mass = mass
        self.physical_radius = physical_radius
        self.ephemeris = ephemeris

    def ephemeris_len(self) -> int:
        return len(self.ephemeris.positions)

    def update_from_ephemeris(self, index: int):
        self.pos = to_vpy_vec(self.ephemeris.positions[index])
        self.velocity = to_vpy_vec(self.ephemeris.velocities[index])

    def integrate(self, dt: float):
        self.velocity += self.acceleration * dt
        self.pos += self.velocity * dt
        self.acceleration = vector(0, 0, 0)

    def apply_force(self, force: vector):
        self.acceleration += force / self.mass

    def grav_force_on_self_by(self, other: "Body") -> vector:
        r_vec = other.pos - self.pos
        r_mag = mag(r_vec)
        if r_mag == 0:
            return vector(0, 0, 0)
        r_hat = r_vec / r_mag
        force_mag = G_val * (other.mass * self.mass) / r_mag**2
        return r_hat * force_mag
