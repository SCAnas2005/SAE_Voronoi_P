from voronoi import Point

def test_point_init():
    # Arrange
    p = Point(2.0, 4.0)
    
    # Act
    assert p.x == 2.0
    assert p.y == 4.0

def test_point_add():
    # Arrange
    p1 = Point(2.0, 4.0)
    p2 = Point(1.0, 3.0)
    
    # Act
    p_res = p1 + p2

    # Assert
    assert p_res.x == 3.0
    assert p_res.y == 7.0

def test_point_sub():
    # Arrange
    p1 = Point(2.0, 4.0)
    p2 = Point(1.0, 3.0)
    
    # Act
    p_res = p1 - p2

    # Assert
    assert p_res.x == 1.0
    assert p_res.y == 1.0

def test_point_mul():
    # Arrange
    p1 = Point(2.0, 4.0)
    
    # Act
    p_res = p1 * 2

    # Assert
    assert p_res.x == 4.0
    assert p_res.y == 8.0

def test_point_truediv():
    # Arrange
    p1 = Point(2.0, 4.0)
    
    # Act
    p_res = p1 / 2

    # Assert
    assert p_res.x == 1.0
    assert p_res.y == 2.0