# **README — Projet Voronoï (Python)**

## **Description du projet**

Ce projet implémente :

- la **triangulation de Delaunay** via l’algorithme de **Bowyer–Watson**,
- la construction du **diagramme de Voronoï** à partir des cercles circonscrits,
- l’affichage graphique avec **matplotlib**,
- l’export possible en **SVG**,
- la lecture des points depuis un fichier externe `points.txt`,
- une architecture modulaire et propre,
- une suite de **tests unitaires** avec `pytest`.

Aucune bibliothèque externe de géométrie (SciPy, Shapely, etc.) n’est utilisée : **tout est implémenté manuellement**, conformément au cahier des charges.

## **Structure du projet**

Code

```
voronoi/
│
├── points.txt
├── README.md
├── pytest.ini
├── requirements.txt
│
├── voronoi_app/
│   ├── __init__.py
│   ├── cli.py
│   ├── io_utils.py
│   ├── geometry.py
│   ├── delaunay.py
│   ├── voronoi.py
│   ├── svg_export.py
│
└── tests/
    ├── test_io_utils.py
    ├── test_geometry.py
    ├── test_delaunay.py
    ├── test_voronoi.py
```

## **Installation**

### 1. Créer un environnement virtuel

```bash
python -m venv venv
```

### 2. Activer le venv

```bash
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Linux / macOS
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

## **Format du fichier** `points.txt`

Le fichier doit contenir **un point par ligne**, sous la forme :

```text
x,y
```

ou

```text
x y
```

Exemple :

```text
0,0
4,0
4,4
0,4
2,1
3,3
```

## **Lancer le programme**

Depuis la racine du projet :

```bash
python -m voronoi_app.cli points.txt
```

Cela :

- lit les points depuis le fichier,
- calcule la triangulation de Delaunay,
- construit le diagramme de Voronoï,
- affiche le résultat avec matplotlib.

## **Lancer les tests**

```bash
pytest
```
