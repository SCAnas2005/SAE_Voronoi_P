import math
from voronoi_app.geometry import circumcircle, point_in_circumcircle

def test_circumcircle_equilateral():
    tri = [(0, 0), (2, 0), (1, math.sqrt(3))]
    center, radius = circumcircle(tri)

    expected_center = (1, math.sqrt(3)/3)
    assert abs(center[0] - expected_center[0]) < 1e-9
    assert abs(center[1] - expected_center[1]) < 1e-9

    expected_radius = 2 / math.sqrt(3)
    assert abs(radius - expected_radius) < 1e-9


def test_point_in_circumcircle_inside():
    tri = [(0, 0), (4, 0), (2, 4)]
    p = (2, 1)
    assert point_in_circumcircle(p, tri)


def test_point_in_circumcircle_outside():
    tri = [(0, 0), (4, 0), (2, 4)]
    p = (10, 10)
    assert not point_in_circumcircle(p, tri)


def test_circumcircle_collinear_points():
    tri = [(0, 0), (1, 1), (2, 2)]  # colinéaires
    center, radius = circumcircle(tri)
    assert radius > 1e6  # cercle "infini"
