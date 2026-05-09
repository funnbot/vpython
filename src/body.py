# why pylance angry?
from astropy.constants import G  # type: ignore
from numpy import sqrt
from vpython import mag, mag2, vector
from vpython.vpython import sphere

from ephemeris import Ephemeris
from linalg import set_vpy_vec, to_vpy_vec

G_val = float(G.to("km3 / (kg s2)").value)


class Body(sphere):
    name: str
    velocity: vector
    acceleration: vector
    mass: float
    physical_radius: float
    ephemeris: Ephemeris

    closest_body: "Body | None" = None

    def __init__(
        self,
        name: str,
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

        self.name = name
        self.velocity = to_vpy_vec(ephemeris.velocities[0])
        self.acceleration = vector(0, 0, 0)
        self.mass = mass
        self.physical_radius = physical_radius
        self.ephemeris = ephemeris

    def ephemeris_len(self) -> int:
        return len(self.ephemeris.positions)

    def update_from_ephemeris(self, index: int):
        set_vpy_vec(self.pos, self.ephemeris.positions[index])
        set_vpy_vec(self.velocity, self.ephemeris.velocities[index])

    def integrate(self, dt: float):
        self.velocity += self.acceleration * dt
        self.pos += self.velocity * dt
        self.acceleration = vector(0, 0, 0)

    def apply_force(self, force: vector):
        self.acceleration += force / self.mass

    def update_closest_body(self, bodies: list["Body"]):
        self.closest_body = find_closest_body(self, bodies)

    def apply_gravity_from_closest(self):
        self.apply_gravity_force(self.closest_body)  # type: ignore

    def apply_gravities(self, others: list["Body"]):
        for other in others:
            if other is self:
                continue

            r_vec = other.pos - self.pos
            r_mag2 = mag2(r_vec)
            if r_mag2 == 0:
                return vector(0, 0, 0)
            force_mag = G_val * other.mass / r_mag2
            self.acceleration += r_vec / sqrt(r_mag2) * force_mag

    def apply_gravity_force(self, other: "Body"):
        r_vec = other.pos - self.pos
        r_mag2 = mag2(r_vec)
        force_mag = G_val * other.mass / r_mag2
        self.acceleration += r_vec / sqrt(r_mag2) * force_mag

    def grav_force_on_self_by(self, other: "Body") -> vector:
        r_vec = other.pos - self.pos
        r_mag2 = mag2(r_vec)
        if r_mag2 == 0:
            return vector(0, 0, 0)
        r_hat = r_vec / sqrt(r_mag2)
        force_mag = (G_val * other.mass) * (self.mass / r_mag2)
        return r_hat * force_mag


def find_closest_body(body: Body, bodies: list[Body]) -> Body:
    closest_body = None
    closest_dist2 = float("inf")
    for other in bodies:
        if other is body:
            continue
        dist2 = mag2(other.pos - body.pos)
        if dist2 < closest_dist2:
            closest_body = other
            closest_dist2 = dist2
    return closest_body  # type: ignore
