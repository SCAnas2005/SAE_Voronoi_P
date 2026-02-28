from voronoi_app.delaunay import bowyer_watson
from voronoi_app.voronoi import build_voronoi

def test_voronoi_centers_exist():
    pts = [(0, 0), (4, 0), (2, 3)]
    triangles = bowyer_watson(pts)
    centers, edges = build_voronoi(triangles)
    assert len(centers) == 1


def test_voronoi_edges_square():
    pts = [(0, 0), (4, 0), (4, 4), (0, 4)]
    triangles = bowyer_watson(pts)
    centers, edges = build_voronoi(triangles)

    first = centers[0]
    assert all(abs(c[0] - first[0]) < 1e-9 and abs(c[1] - first[1]) < 1e-9 for c in centers)


def test_voronoi_edges_connect_centers():
    pts = [(0, 0), (4, 0), (4, 4), (0, 4)]
    triangles = bowyer_watson(pts)
    centers, edges = build_voronoi(triangles)

    for a, b in edges:
        assert a in centers
        assert b in centers
