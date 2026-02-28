import sys
import matplotlib.pyplot as plt
from typing import List, Tuple

from voronoi_app.io_utils import load_points_from_file
from voronoi_app.delaunay import bowyer_watson
from voronoi_app.voronoi import build_voronoi

Point = Tuple[float, float]


def main() -> None:
    """
    Lit un fichier de points, calcule Delaunay + Voronoï, et affiche le résultat.
    """

    if len(sys.argv) != 2:
        print("Usage : python -m voronoi_app.cli <points.txt>")
        sys.exit(1)

    filename = sys.argv[1]

    # Charger les points depuis le fichier
    points: List[Point] = load_points_from_file(filename)

    # Triangulation de Delaunay
    triangles = bowyer_watson(points)

    # Diagramme de Voronoï
    centers, edges = build_voronoi(triangles)

    fig, ax = plt.subplots()

    # Arêtes du Voronoï
    for a, b in edges:
        ax.plot([a[0], b[0]], [a[1], b[1]],
                color="black", linewidth=1.0)

    # Points
    xs, ys = zip(*points)
    ax.plot(xs, ys, "o", color="tab:blue", markersize=5)

    ax.set_aspect("equal")
    ax.set_xlim(min(xs) - 1, max(xs) + 1)
    ax.set_ylim(min(ys) - 1, max(ys) + 1)

    plt.show()


if __name__ == "__main__":
    main()
