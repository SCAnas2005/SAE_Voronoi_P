from typing import List, Tuple

from voronoi_app.geometry import point_in_circumcircle

Point = Tuple[float, float]
Triangle = Tuple[Point, Point, Point]


def bowyer_watson(points: List[Point]) -> List[Triangle]:
    """
    Algorithme de Bowyer-Watson pour construire la triangulation de Delaunay
    à partir d'une liste de points.
    Retourne une liste de triangles (triplets de points).
    """
    if len(points) < 3:
        return []

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    dx = xmax - xmin
    dy = ymax - ymin
    dmax = max(dx, dy) * 10

    p1: Point = (xmin - dmax, ymin - dmax)
    p2: Point = (xmin + 2 * dmax, ymin - dmax)
    p3: Point = (xmin - dmax, ymin + 2 * dmax)

    triangles: List[Triangle] = [(p1, p2, p3)]

    for p in points:
        bad: List[Triangle] = []
        for tri in triangles:
            if point_in_circumcircle(p, tri):
                bad.append(tri)

        # Arêtes du "trou"
        edges: List[Tuple[Point, Point]] = []
        for (a, b, c) in bad:
            tri_edges = [(a, b), (b, c), (c, a)]
            for e in tri_edges:
                e_sorted = tuple(sorted(e))
                if e_sorted in edges:
                    edges.remove(e_sorted)
                else:
                    edges.append(e_sorted)

        for t in bad:
            triangles.remove(t)

        for (a, b) in edges:
            triangles.append((a, b, p))

    # Retirer les triangles qui utilisent le super-triangle
    final: List[Triangle] = []
    super_pts = {p1, p2, p3}
    for tri in triangles:
        if any(v in super_pts for v in tri):
            continue
        final.append(tri)

    return final
