import tempfile
from voronoi_app.io_utils import load_points_from_file

def test_load_points_basic():
    content = "1,2\n3,4\n5,6\n"
    with tempfile.NamedTemporaryFile("w+", delete=False) as f:
        f.write(content)
        fname = f.name

    pts = load_points_from_file(fname)
    assert pts == [(1,2), (3,4), (5,6)]

def test_load_points_spaces():
    content = "1 2\n3 4\n"
    with tempfile.NamedTemporaryFile("w+", delete=False) as f:
        f.write(content)
        fname = f.name

    pts = load_points_from_file(fname)
    assert pts == [(1,2), (3,4)]

def test_load_points_invalid():
    content = "1,2,3\n"
    with tempfile.NamedTemporaryFile("w+", delete=False) as f:
        f.write(content)
        fname = f.name

    try:
        load_points_from_file(fname)
        assert False, "Should raise ValueError"
    except ValueError:
        pass
