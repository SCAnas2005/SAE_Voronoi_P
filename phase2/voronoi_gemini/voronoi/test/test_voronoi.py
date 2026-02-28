import pytest
from voronoi.voronoi_app.geometry import GeometryUtils, VoronoiClipper

def test_squared_distance_calculation():
    point_origin = (0, 0)
    point_target = (3, 4)
    assert GeometryUtils.calculate_squared_distance(point_origin, point_target) == 25

def test_clipping_of_boundary_cell():
    clipper = VoronoiClipper(bounding_box=(0, 0, 10, 10))
    initial_cell = clipper.generate_initial_bounding_cell()
    
    # Points situés horizontalement pour créer une médiatrice verticale à x=5
    left_point = (4, 5)
    right_point = (6, 5)
    
    clipped_cell = clipper.clip_cell_by_neighbor(initial_cell, left_point, right_point)
    
    # On vérifie que tous les points résultants sont bien dans la zone du left_point (x <= 5)
    for vertex_x, vertex_y in clipped_cell:
        assert vertex_x <= 5.000001