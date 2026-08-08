"""Evolvable 26-circle packing scaffold for a unit square."""

from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np

N_CIRCLES = 26
MIN_RADIUS = 1e-6


Point = tuple[float, float]


PACKING_LAYOUT: tuple[tuple[float, float, float], ...] = (
    (0.1107790127519884, 0.1107790127519884, 0.11077901285148839),
    (0.3167414650086849, 0.09573232926679698, 0.09573232936629697),
    (0.5153991973496163, 0.10306052010208701, 0.103060520201587),
    (0.7252167166715885, 0.10679014458945663, 0.10679014468895662),
    (0.9153604993455553, 0.08463950065444471, 0.0846395007539447),
    (0.09239155153040181, 0.3131158099518068, 0.0923915516299018),
    (0.2575829504742439, 0.40335878359306515, 0.09584232580479103),
    (0.4023652036026225, 0.27162985146327867, 0.09989835065244458),
    (0.6130764466016491, 0.2947460590285266, 0.1120770890111578),
    (0.8697788989715687, 0.29460948876139054, 0.1302211011279314),
    (0.09392733723703926, 0.4994283691389825, 0.09392733733653925),
    (0.25795055651532367, 0.595219732949207, 0.09601897581755771),
    (0.4700365802438266, 0.4986680755032695, 0.13701043018713013),
    (0.7246573832509132, 0.49553176067391225, 0.11762968810799594),
    (0.9211396271259397, 0.49728444620383916, 0.07886037297356034),
    (0.09259209491089837, 0.685943022005284, 0.09259209501039836),
    (0.23704113631983703, 0.7593524015867373, 0.06944019376791766),
    (0.40395729808230857, 0.726905714334173, 0.10060036787847113),
    (0.6183341555591282, 0.7026096037191839, 0.11514888022123028),
    (0.8667414272656793, 0.7023095251092896, 0.13325857283382084),
    (0.11115617937175491, 0.8888438206282451, 0.1111561794712549),
    (0.3179199570492925, 0.9038486659944179, 0.09615133410508205),
    (0.5174044177911892, 0.8965327666815028, 0.10346723341799718),
    (0.7260471603985392, 0.8948174397705353, 0.1051825603289647),
    (0.9150737375864008, 0.9150737375864008, 0.08492626251309923),
    (0.23632643059037875, 0.23971052790163774, 0.06918067641386796),
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


def run_packing() -> tuple[list[Point], list[float], float]:
    """Stable entrypoint used by the evaluator."""
    centers, radii = construct_packing()
    return centers, radii, float(sum(radii))


__all__ = ["MIN_RADIUS", "N_CIRCLES", "Point", "construct_packing", "run_packing"]
