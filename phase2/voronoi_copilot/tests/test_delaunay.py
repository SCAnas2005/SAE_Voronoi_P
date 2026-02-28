from voronoi_app.delaunay import bowyer_watson
from voronoi_app.voronoi import build_voronoi

def test_delaunay_simple_triangle():
    pts = [(0, 0), (4, 0), (2, 3)]
    triangles = bowyer_watson(pts)
    assert len(triangles) == 1
    assert set(triangles[0]) == set(pts)


def test_delaunay_not_enough_points():
    assert bowyer_watson([]) == []
    assert bowyer_watson([(1,1)]) == []
    assert bowyer_watson([(1,1),(2,2)]) == []


def test_delaunay_random_points():
    import random
    pts = [(random.random()*10, random.random()*10) for _ in range(20)]
    triangles = bowyer_watson(pts)
    assert len(triangles) > 0


def test_voronoi_edges_square():
    pts = [(0, 0), (4, 0), (4, 4), (0, 4)]
    triangles = bowyer_watson(pts)
    centers, edges = build_voronoi(triangles)

    assert len(edges) >= 1

    c = edges[0][0]
    assert abs(c[0] - 2) < 1e-9
    assert abs(c[1] - 2) < 1e-9
