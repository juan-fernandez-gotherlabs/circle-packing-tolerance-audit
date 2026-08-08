"""Evolvable 26-circle packing scaffold for a unit square."""

from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np

N_CIRCLES = 26
MIN_RADIUS = 1e-6


Point = tuple[float, float]


PACKING_LAYOUT: tuple[tuple[float, float, float], ...] = (
    (0.1107786235699233, 0.1107786235699233, 0.11077962356942331),
    (0.31674128176847577, 0.09573192503955305, 0.09573292503905306),
    (0.5153992127472737, 0.1030601232023011, 0.10306112320180111),
    (0.7252169418657834, 0.10678975141892225, 0.10679075141842226),
    (0.9153609146645186, 0.08463908533548146, 0.08464008533498148),
    (0.09239114396271424, 0.31311562308630525, 0.09239214396221425),
    (0.25758270808143613, 0.40335868696151295, 0.09584292158753258),
    (0.4023651059775897, 0.2716296231159672, 0.09989895049080537),
    (0.613076559666788, 0.29474585379511103, 0.11207770102703907),
    (0.8697792687134898, 0.2946092833914184, 0.13022173128601033),
    (0.09392693120498381, 0.49942836856740885, 0.09392793120448382),
    (0.25795031449008515, 0.5952198281594181, 0.09601957177693159),
    (0.47003655028340324, 0.49866807417147824, 0.13701106713385922),
    (0.7246576078858307, 0.4955317562061198, 0.11763030567592105),
    (0.9211400482234529, 0.49728444348855694, 0.07886095177604725),
    (0.09259168754373412, 0.6859432079297118, 0.09259268754323413),
    (0.2370408733872693, 0.7593526609132036, 0.06944076315116737),
    (0.403957202049211, 0.7269059412171966, 0.10060096841877894),
    (0.6183342738814503, 0.7026098063085267, 0.11514949530859558),
    (0.8667417939704324, 0.7023097273985838, 0.13325920602906774),
    (0.11115579056681871, 0.8888442094331813, 0.11115679056631872),
    (0.3179197749874576, 0.9038490698026991, 0.09615193019680097),
    (0.5174044351938666, 0.8965331631746163, 0.10346783682488384),
    (0.726047386423095, 0.8948178345484933, 0.10518316545100674),
    (0.915074152618631, 0.915074152618631, 0.08492684738086909),
    (0.23632616694317676, 0.23971026763819467, 0.06918124553762627),
)


def _clip01(value: float, *, eps: float = 1e-6) -> float:
    """Clamp a coordinate to the open unit square."""
    return min(1.0 - eps, max(eps, float(value)))


def _distance(a: Point, b: Point) -> float:
    """Return Euclidean distance between two points."""
    return math.hypot(float(a[0]) - float(b[0]), float(a[1]) - float(b[1]))


# EVOLVE_START: construct_packing
def construct_packing() -> tuple[list[Point], list[float]]:
    """Construct 26 circle centers and radii inside the unit square.

    Contract:
        * Return exactly 26 centers and 26 radii.
        * Centers must be finite ``(x, y)`` pairs in ``[0, 1]``.
        * Radii must be finite and strictly greater than ``1e-6``.
        * Circles must not overlap and must stay inside the unit square.
        * Keep the implementation deterministic. Avoid I/O and global randomness.
    """
    centers = [(float(x), float(y)) for x, y, _ in PACKING_LAYOUT]
    radii = [float(r) for _, _, r in PACKING_LAYOUT]
    return centers, radii


def compute_max_radii(centers: Sequence[Point]) -> list[float]:
    """Compute conservative non-overlapping radii for fixed centers."""
    centers_array = np.asarray(centers, dtype=float)
    n = centers_array.shape[0]
    radii = np.ones(n, dtype=float)

    for i in range(n):
        x, y = centers_array[i]
        radii[i] = min(float(x), float(y), 1.0 - float(x), 1.0 - float(y))

    for _ in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                dist = float(np.sqrt(np.sum((centers_array[i] - centers_array[j]) ** 2)))
                if radii[i] + radii[j] > dist and radii[i] + radii[j] > 0.0:
                    scale = dist / (radii[i] + radii[j])
                    radii[i] *= scale
                    radii[j] *= scale

    radii = np.maximum(radii, MIN_RADIUS * 1.001)
    return [float(radius) for radius in radii]


# EVOLVE_END


def run_packing() -> tuple[np.ndarray, np.ndarray, float]:
    """Stable entrypoint used by the public evaluator."""
    centers, radii = construct_packing()
    centers_array = np.asarray(centers, dtype=float)
    radii_array = np.asarray(radii, dtype=float)
    return centers_array, radii_array, float(np.sum(radii_array))


__all__ = ["MIN_RADIUS", "N_CIRCLES", "Point", "construct_packing", "run_packing"]
