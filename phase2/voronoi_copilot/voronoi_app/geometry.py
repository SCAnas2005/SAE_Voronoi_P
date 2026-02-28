import math
from typing import Tuple

Point = Tuple[float, float]
Triangle = Tuple[Point, Point, Point]


def circumcircle(tri: Triangle) -> Tuple[Point, float]:
    """
    Calcule le cercle circonscrit d'un triangle.
    Retourne (centre, rayon).
    """
    (x1, y1), (x2, y2), (x3, y3) = tri

    d = 2 * (
            x1 * (y2 - y3)
            + x2 * (y3 - y1)
            + x3 * (y1 - y2)
    )

    if abs(d) < 1e-12:
        cx = (x1 + x2 + x3) / 3
        cy = (y1 + y2 + y3) / 3
        r = 1e12
        return (cx, cy), r

    ux = (
                 (x1**2 + y1**2) * (y2 - y3)
                 + (x2**2 + y2**2) * (y3 - y1)
                 + (x3**2 + y3**2) * (y1 - y2)
         ) / d

    uy = (
                 (x1**2 + y1**2) * (x3 - x2)
                 + (x2**2 + y2**2) * (x1 - x3)
                 + (x3**2 + y3**2) * (x2 - x1)
         ) / d

    cx, cy = ux, uy
    r = math.hypot(cx - x1, cy - y1)
    return (cx, cy), r


def point_in_circumcircle(p: Point, tri: Triangle) -> bool:
    """
    Indique si un point p est strictement à l'intérieur du cercle circonscrit
    au triangle tri.
    """
    (cx, cy), r = circumcircle(tri)
    x, y = p
    return (x - cx) ** 2 + (y - cy) ** 2 < r**2 - 1e-12
