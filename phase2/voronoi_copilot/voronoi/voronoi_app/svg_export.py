from typing import List, Tuple

import drawsvg as draw

Point = Tuple[float, float]
Polygon = List[Point]


def export_voronoi_graph_svg(
        points: List[Point],
        centers: List[Point],
        edges: List[Tuple[Point, Point]],
        filename: str = "voronoi_graph.svg",
) -> None:
    """
    Exporte le graphe de Voronoï (centres + arêtes) en SVG.
    """
    xs = [p[0] for p in points] + [c[0] for c in centers]
    ys = [p[1] for p in points] + [c[1] for c in centers]

    xmin, xmax = min(xs) - 1, max(xs) + 1
    ymin, ymax = min(ys) - 1, max(ys) + 1
    width = xmax - xmin
    height = ymax - ymin

    d = draw.Drawing(width, height, origin=(xmin, ymin), display_inline=False)

    # Arêtes du Voronoï
    for a, b in edges:
        d.append(
            draw.Line(
                a[0],
                a[1],
                b[0],
                b[1],
                stroke="green",
                stroke_width=0.03,
            )
        )

    # Points
    for x, y in points:
        d.append(draw.Circle(x, y, 0.07, fill="blue"))

    d.save_svg(filename)


def export_voronoi_cells_svg(
        points: List[Point],
        cells: List[Polygon],
        filename: str = "voronoi_cells.svg",
) -> None:
    """
    Exporte les cellules de Voronoï (polygones) en SVG.
    """
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    for poly in cells:
        for (x, y) in poly:
            xs.append(x)
            ys.append(y)

    xmin, xmax = min(xs) - 1, max(xs) + 1
    ymin, ymax = min(ys) - 1, max(ys) + 1
    width = xmax - xmin
    height = ymax - ymin

    d = draw.Drawing(width, height, origin=(xmin, ymin), display_inline=False)

    # Cellules
    for poly in cells:
        if len(poly) < 3:
            continue
        d.append(
            draw.Lines(
                *[coord for xy in poly for coord in xy],
                close=True,
                fill="none",
                stroke="green",
                stroke_width=0.03,
            )
        )

    # Points
    for x, y in points:
        d.append(draw.Circle(x, y, 0.07, fill="blue"))

    d.save_svg(filename)
