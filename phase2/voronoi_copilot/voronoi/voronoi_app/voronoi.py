import math
from typing import Dict, List, Tuple

from voronoi_app.geometry import circumcircle

Point = Tuple[float, float]
Triangle = Tuple[Point, Point, Point]
Polygon = List[Point]


def build_voronoi(triangles: List[Triangle]) -> Tuple[List[Point], List[Tuple[Point, Point]]]:
    """
    Construit les centres des cercles circonscrits et les arêtes du diagramme
    de Voronoï (graphe dual de Delaunay).

    triangles : liste de triangles, chaque triangle = ((x1,y1),(x2,y2),(x3,y3))
    Retourne : (centers, edges)
    """
    centers: List[Point] = [circumcircle(tri)[0] for tri in triangles]

    edges: List[Tuple[Point, Point]] = []
    n = len(triangles)
    for i in range(n):
        for j in range(i + 1, n):
            if len(set(triangles[i]) & set(triangles[j])) == 2:
                edges.append((centers[i], centers[j]))

    return centers, edges


def build_voronoi_cells(points: List[Point], triangles: List[Triangle]) -> List[Polygon]:
    """
    Construit les cellules de Voronoï pour chaque point.
    Retourne une liste de polygones (liste de points).
    """
    centers: List[Point] = []
    for tri in triangles:
        center, _ = circumcircle(tri)
        centers.append(center)

    point_to_centers: Dict[Point, List[Point]] = {p: [] for p in points}

    for idx, tri in enumerate(triangles):
        for p in tri:
            point_to_centers[p].append(centers[idx])

    cells: List[Polygon] = []
    for p in points:
        cx_list = point_to_centers[p]

        if len(cx_list) < 2:
            cells.append([])
            continue

        px, py = p

        cx_list_sorted = sorted(
            cx_list,
            key=lambda c: math.atan2(c[1] - py, c[0] - px),
        )

        cells.append(cx_list_sorted)

    return cells
