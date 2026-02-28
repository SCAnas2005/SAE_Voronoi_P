from typing import List, Tuple

Point = Tuple[float, float]

def load_points_from_file(filename: str) -> List[Point]:
    """
    Charge une liste de points depuis un fichier texte.
    Format accepté : x,y ou x y
    Une ligne = un point.
    """
    points: List[Point] = []

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Autoriser x,y ou x y
            line = line.replace(",", " ")
            parts = line.split()

            if len(parts) != 2:
                raise ValueError(f"Ligne invalide : '{line}' (format attendu : x,y ou x y)")

            x, y = map(float, parts)
            points.append((x, y))

    return points
