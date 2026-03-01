# Diagramme de Voronoï

Générateur de diagramme de Voronoï avec interface graphique interactive, implémenté from scratch en Python avec l'**algorithme de Fortune** (sweep line, O(n log n)).

![Python](https://img.shields.io/badge/Python-3.9+-blue) ![License](https://img.shields.io/badge/license-MIT-green)

---

## Prérequis

- Python 3.9 ou supérieur
- `tkinter` — inclus avec Python sur Windows et macOS. Sur Linux :
  ```bash
  sudo apt install python3-tk
  ```

---

## Installation

```bash
# 1. Cloner ou télécharger le projet
cd voronoi_claude

# 2. (Optionnel) Créer un environnement virtuel
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows

# 3. Installer les dépendances
pip install -r requirements.txt
```

---

## Lancer le programme

```bash
python voronoi_gui.py
```

Ou en chargeant directement un fichier de points au démarrage :

```bash
python voronoi_gui.py points.txt
```

---

## Utilisation de l'interface

| Action | Résultat |
|---|---|
| **Clic gauche** sur le canvas | Ajoute un point, le diagramme se recalcule instantanément |
| **Clic droit** sur un point | Supprime le point le plus proche du curseur |
| **Molette / barre de navigation** | Zoom et déplacement |
| **Charger fichier** | Importe des points depuis un fichier `.txt` ou `.csv` |
| **Points aléatoires** | Génère entre 8 et 20 points aléatoires |
| **Effacer tout** | Remet le canvas à zéro |
| **Exporter PNG** | Sauvegarde l'image en PNG, SVG ou PDF |
| **Slider Opacité** | Ajuste la transparence des cellules colorées |

---

## Format du fichier de points

Un point par ligne, coordonnées séparées par une virgule ou un point-virgule. Les lignes commençant par `#` sont ignorées.

```
# Mon fichier de points
100, 150
250, 80
400, 200
180.5, 320.7
```

---

## Lancer les tests

```bash
pytest test_voronoi.py -v
```

61 tests couvrant :
- Les structures de données (`Point`, `Event`, `Arc`)
- L'algorithme géométrique (`circumcenter`, `_par_inter`)
- Le clipping Cohen-Sutherland (`clip_seg`)
- La structure du diagramme (nombre de faces, d'arêtes, sommets)
- Les propriétés mathématiques (équidistance, perpendicularité, cellule NN)
- La lecture de fichiers (formats, commentaires, lignes malformées)
- Les cas limites (points proches, colinéaires, en cercle, grands nombres)

---

## Structure du projet

```
voronoi_claude/
├── voronoi_gui.py      # Programme principal (algorithme + interface)
├── test_voronoi.py     # Suite de tests pytest (61 tests)
├── requirements.txt    # Dépendances Python
├── README.md           # Ce fichier
└── points.txt          # Exemple de fichier de points (optionnel)
```

---

## Algorithme

L'algorithme de **Fortune** calcule le diagramme de Voronoï en balayant le plan de gauche à droite avec une *sweep line* :

- Une **file de priorité** (min-heap) traite les *site events* et les *circle events*
- La **beach line** est une liste doublement liée d'arcs de parabole
- La **DCEL** (Doubly Connected Edge List) stocke la topologie du diagramme
- Le clipping **Cohen-Sutherland** borne les arêtes semi-infinies

Complexité : **O(n log n)** en temps, **O(n)** en mémoire.
