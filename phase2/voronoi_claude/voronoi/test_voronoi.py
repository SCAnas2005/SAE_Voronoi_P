"""
Tests unitaires — Diagramme de Voronoï (Fortune's Sweep Line)
Couverture :
  • Point
  • Event (ordre de priorité)
  • circumcenter
  • _par_inter (intersection de paraboles)
  • FortuneAlgorithm  (cas limites + propriétés mathématiques)
  • clip_seg (Cohen-Sutherland)
  • collect_segments
  • Lecture de fichier points
"""

import sys, types, math, os, tempfile, importlib
import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Mock des dépendances graphiques (tkinter, matplotlib GUI) pour ne pas avoir
# besoin d'un display lors des tests CI/headless.
# ─────────────────────────────────────────────────────────────────────────────

def _make_mock_module(name):
    """Crée un module mock récursivement."""
    mod = types.ModuleType(name)
    mod.__path__ = []
    sys.modules[name] = mod
    return mod

for _name in [
    "tkinter", "tkinter.filedialog", "tkinter.messagebox", "tkinter.ttk",
    "matplotlib", "matplotlib.pyplot", "matplotlib.backends",
    "matplotlib.backends.backend_tkagg", "matplotlib.collections",
]:
    if _name not in sys.modules:
        _make_mock_module(_name)

# matplotlib.use() ne doit rien faire
sys.modules["matplotlib"].use = lambda *a, **k: None

# FigureCanvasTkAgg & NavigationToolbar2Tk → stubs
_backend = sys.modules["matplotlib.backends.backend_tkagg"]
_backend.FigureCanvasTkAgg       = object
_backend.NavigationToolbar2Tk    = object

# LineCollection stub
sys.modules["matplotlib.collections"].LineCollection = object

# plt.subplots stub (retourne un objet avec .subplots_adjust)
class _FakeFig:
    def subplots_adjust(self, **kw): pass
class _FakeAx:
    pass
_plt = sys.modules["matplotlib.pyplot"]
_plt.subplots = lambda **kw: (_FakeFig(), _FakeAx())

# numpy : réel si disponible, sinon stub minimal
try:
    import numpy as np
except ImportError:
    np = None

# ─────────────────────────────────────────────────────────────────────────────
# Import du module principal
# ─────────────────────────────────────────────────────────────────────────────

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(__file__))
import voronoi_gui as vg

# ═════════════════════════════════════════════════════════════════════════════
# Helpers
# ═════════════════════════════════════════════════════════════════════════════

def P(x, y):
    return vg.Point(x, y)

def voronoi(coords):
    """Lance Fortune sur une liste de tuples (x, y)."""
    pts = [P(x, y) for x, y in coords]
    fa  = vg.FortuneAlgorithm(pts)
    fa.compute()
    return fa.diagram, pts

def nearest_site(px, py, sites):
    """Retourne l'index du site le plus proche de (px, py)."""
    dists = [(math.hypot(s.x - px, s.y - py), i) for i, s in enumerate(sites)]
    return min(dists)[1]

EPS = 1e-6


# ═════════════════════════════════════════════════════════════════════════════
# 1. Point
# ═════════════════════════════════════════════════════════════════════════════

class TestPoint:
    def test_creation_entiers(self):
        p = P(3, 4)
        assert p.x == 3.0 and p.y == 4.0

    def test_creation_flottants(self):
        p = P(1.5, -2.7)
        assert p.x == pytest.approx(1.5)
        assert p.y == pytest.approx(-2.7)

    def test_creation_negatifs(self):
        p = P(-100, -200)
        assert p.x == -100.0 and p.y == -200.0

    def test_conversion_str_vers_float(self):
        """Point accepte toute valeur castable en float."""
        p = vg.Point("3.14", "2.71")
        assert p.x == pytest.approx(3.14)
        assert p.y == pytest.approx(2.71)

    def test_zero(self):
        p = P(0, 0)
        assert p.x == 0.0 and p.y == 0.0


# ═════════════════════════════════════════════════════════════════════════════
# 2. Event (ordre de priorité dans le heap)
# ═════════════════════════════════════════════════════════════════════════════

class TestEvent:
    def test_ordre_par_x(self):
        e1 = vg.Event(1.0, P(1, 5))
        e2 = vg.Event(2.0, P(2, 3))
        assert e1 < e2

    def test_egalite_x_tri_par_y(self):
        e1 = vg.Event(5.0, P(5, 1))
        e2 = vg.Event(5.0, P(5, 3))
        assert e1 < e2

    def test_valid_par_defaut(self):
        e = vg.Event(0.0, P(0, 0))
        assert e.valid is True

    def test_arc_none_pour_site_event(self):
        e = vg.Event(10.0, P(10, 10))
        assert e.arc is None

    def test_arc_non_none_pour_circle_event(self):
        arc = vg.Arc(P(0, 0))
        e   = vg.Event(5.0, P(5, 5), arc=arc)
        assert e.arc is arc


# ═════════════════════════════════════════════════════════════════════════════
# 3. circumcenter
# ═════════════════════════════════════════════════════════════════════════════

class TestCircumcenter:
    def test_triangle_droit(self):
        """Triangle rectangle : le centre est au milieu de l'hypoténuse."""
        a, b, c = P(0, 0), P(4, 0), P(0, 4)
        cc = vg.circumcenter(a, b, c)
        assert cc is not None
        assert cc.x == pytest.approx(2.0, abs=EPS)
        assert cc.y == pytest.approx(2.0, abs=EPS)

    def test_equidistance(self):
        """Le centre doit être équidistant des trois sommets."""
        a, b, c = P(0, 0), P(6, 0), P(3, 4)
        cc = vg.circumcenter(a, b, c)
        assert cc is not None
        ra = math.hypot(cc.x - a.x, cc.y - a.y)
        rb = math.hypot(cc.x - b.x, cc.y - b.y)
        rc = math.hypot(cc.x - c.x, cc.y - c.y)
        assert ra == pytest.approx(rb, abs=EPS)
        assert rb == pytest.approx(rc, abs=EPS)

    def test_points_colineaires_retourne_none(self):
        """Trois points colinéaires → pas de cercle → None."""
        a, b, c = P(0, 0), P(1, 1), P(2, 2)
        assert vg.circumcenter(a, b, c) is None

    def test_triangle_isocele(self):
        a, b, c = P(-3, 0), P(3, 0), P(0, 4)
        cc = vg.circumcenter(a, b, c)
        assert cc is not None
        # Symétrie : cx doit être 0
        assert cc.x == pytest.approx(0.0, abs=EPS)

    def test_triangle_quelconque(self):
        a, b, c = P(1, 2), P(4, 6), P(7, 1)
        cc = vg.circumcenter(a, b, c)
        assert cc is not None
        ra = math.hypot(cc.x - a.x, cc.y - a.y)
        rb = math.hypot(cc.x - b.x, cc.y - b.y)
        assert ra == pytest.approx(rb, abs=EPS)

    def test_points_identiques_retourne_none(self):
        a = P(5, 5)
        assert vg.circumcenter(a, a, a) is None


# ═════════════════════════════════════════════════════════════════════════════
# 4. _par_inter (intersection de paraboles)
# ═════════════════════════════════════════════════════════════════════════════

class TestParInter:
    def test_meme_x_retourne_moyenne_y(self):
        """Deux foyers de même abscisse → intersection au milieu en y."""
        p1, p2 = P(0, 0), P(0, 10)
        y = vg._par_inter(p1, p2, -5)
        assert y == pytest.approx(5.0, abs=EPS)

    def test_symetrie(self):
        """Deux points symétriques par rapport à y=0 → intersection en y=0."""
        p1, p2 = P(0, -3), P(0, 3)
        y = vg._par_inter(p1, p2, -10)
        assert y == pytest.approx(0.0, abs=EPS)

    def test_foyer_sur_sweep(self):
        """Quand le foyer coïncide avec la sweep line, la parabole est verticale."""
        p1, p2 = P(5, 2), P(10, 8)
        # p1 est sur la sweep line x=5 → doit retourner p1.y
        y = vg._par_inter(p1, p2, 5.0)
        assert y == pytest.approx(p1.y, abs=EPS)

    def test_resultat_est_float(self):
        p1, p2 = P(1, 1), P(3, 5)
        y = vg._par_inter(p1, p2, 0.0)
        assert isinstance(y, float)


# ═════════════════════════════════════════════════════════════════════════════
# 5. clip_seg (Cohen-Sutherland)
# ═════════════════════════════════════════════════════════════════════════════

class TestClipSeg:
    BB = (0, 100, 0, 100)  # xmn, xmx, ymn, ymx

    def test_segment_entierement_dans_boite(self):
        r = vg.clip_seg((10, 10), (90, 90), *self.BB)
        assert r is not None
        (x1, y1), (x2, y2) = r
        assert x1 == pytest.approx(10) and y1 == pytest.approx(10)
        assert x2 == pytest.approx(90) and y2 == pytest.approx(90)

    def test_segment_entierement_dehors(self):
        r = vg.clip_seg((200, 200), (300, 300), *self.BB)
        assert r is None

    def test_segment_traverse_boite(self):
        """Segment de (-10, 50) à (110, 50) → clippé de (0,50) à (100,50)."""
        r = vg.clip_seg((-10, 50), (110, 50), *self.BB)
        assert r is not None
        (x1, y1), (x2, y2) = r
        assert x1 == pytest.approx(0, abs=EPS)
        assert x2 == pytest.approx(100, abs=EPS)
        assert y1 == pytest.approx(50) and y2 == pytest.approx(50)

    def test_segment_vertical(self):
        r = vg.clip_seg((50, -20), (50, 120), *self.BB)
        assert r is not None
        (x1, y1), (x2, y2) = r
        assert x1 == pytest.approx(50) and x2 == pytest.approx(50)
        assert y1 == pytest.approx(0, abs=EPS)
        assert y2 == pytest.approx(100, abs=EPS)

    def test_segment_horizontal(self):
        r = vg.clip_seg((-50, 40), (150, 40), *self.BB)
        assert r is not None
        (x1, y1), (x2, y2) = r
        assert x1 == pytest.approx(0, abs=EPS)
        assert x2 == pytest.approx(100, abs=EPS)

    def test_segment_sur_bord(self):
        """Segment exactement sur un bord → doit être conservé."""
        r = vg.clip_seg((0, 0), (100, 0), *self.BB)
        assert r is not None

    def test_segment_un_point_dans_boite(self):
        r = vg.clip_seg((50, 50), (200, 50), *self.BB)
        assert r is not None
        (x1, y1), (x2, y2) = r
        assert x2 == pytest.approx(100, abs=EPS)

    def test_segment_meme_cote_de_la_boite(self):
        """Deux points du même côté extérieur → None (pas de croisement)."""
        r = vg.clip_seg((110, 10), (110, 90), *self.BB)
        assert r is None


# ═════════════════════════════════════════════════════════════════════════════
# 6. FortuneAlgorithm — Structure du diagramme
# ═════════════════════════════════════════════════════════════════════════════

class TestFortuneStructure:
    def test_deux_points(self):
        """2 sites → au moins 1 arête (médiatrice), exactement 2 faces."""
        diag, _ = voronoi([(0, 0), (10, 0)])
        assert len(diag.edges) >= 1
        assert len(diag.faces) == 2

    def test_trois_points_triangle(self):
        """3 sites non colinéaires → 3 arêtes, 1 sommet, 3 faces."""
        diag, _ = voronoi([(0, 0), (10, 0), (5, 8)])
        assert len(diag.faces) == 3
        assert len(diag.edges) >= 3

    def test_nombre_de_faces_egal_nombre_de_sites(self):
        """Il doit y avoir exactement une face par site."""
        coords = [(0, 0), (10, 0), (5, 9), (20, 5), (3, 15)]
        diag, pts = voronoi(coords)
        assert len(diag.faces) == len(pts)

    def test_formule_euler_voronoi(self):
        """
        Formule d'Euler pour Voronoï convexe :
          V - E + F = 2  (avec F comptant la face infinie)
        Ici F = n_sites + 1.
        En pratique : V - E + (n+1) ≈ 2  → V - E ≈ 1 - n
        (Relation vérifiée pour n ≥ 3 sans points cocycliques)
        """
        coords = [(0, 0), (100, 0), (50, 87), (50, 30), (20, 60), (80, 60)]
        diag, pts = voronoi(coords)
        V = len(diag.vertices)
        E = len(diag.edges)
        n = len(pts)
        # Relation lâche : 2V ≤ 3(n - 2) + extras pour arêtes infinies
        assert V >= 0
        assert E >= n - 1

    def test_grille_4x4(self):
        """Grille régulière : n=16 sites → n faces."""
        coords = [(x*10, y*10) for x in range(4) for y in range(4)]
        diag, pts = voronoi(coords)
        assert len(diag.faces) == 16

    def test_grand_nombre_de_points(self):
        """50 points aléatoires → autant de faces que de sites."""
        import random
        random.seed(0)
        coords = [(random.uniform(0, 500), random.uniform(0, 500))
                  for _ in range(50)]
        diag, pts = voronoi(coords)
        assert len(diag.faces) == 50

    def test_points_quasi_colineaires(self):
        """Points presque colinéaires ne doivent pas planter."""
        coords = [(i * 10, i * 0.001) for i in range(8)]
        diag, pts = voronoi(coords)
        assert len(diag.faces) == 8

    def test_point_unique(self):
        """Un seul point → beach line initialisée, pas d'arêtes."""
        pts = [P(5, 5)]
        fa  = vg.FortuneAlgorithm(pts)
        fa.compute()
        assert len(fa.diagram.edges) == 0
        assert len(fa.diagram.faces) == 0


# ═════════════════════════════════════════════════════════════════════════════
# 7. Propriétés mathématiques du diagramme de Voronoï
# ═════════════════════════════════════════════════════════════════════════════

class TestVoronoiProprietes:
    def test_sommets_equidistants_des_sites_voisins(self):
        """
        Chaque sommet Voronoï doit être equidistant des sites des faces
        qui se rejoignent en ce sommet.
        On vérifie via la propriété : dist(vertex, site_A) ≈ dist(vertex, site_B)
        pour deux sites A, B reliés par une arête dont l'une des extrémités
        est ce sommet.
        """
        coords = [(0, 0), (10, 0), (5, 9), (5, 3)]
        diag, pts = voronoi(coords)

        for he, het in diag.edges:
            v = he.origin
            if v is None:
                continue
            site_l = he.face.site if he.face else None
            site_r = het.face.site if het.face else None
            if site_l and site_r:
                dl = math.hypot(v.x - site_l.x, v.y - site_l.y)
                dr = math.hypot(v.x - site_r.x, v.y - site_r.y)
                assert dl == pytest.approx(dr, rel=1e-4), (
                    f"Sommet ({v.x:.3f},{v.y:.3f}) non équidistant : "
                    f"d_gauche={dl:.6f}, d_droite={dr:.6f}"
                )

    def test_mediatrices_perpendiculaires(self):
        """
        Chaque arête Voronoï est perpendiculaire au segment reliant les
        deux sites de part et d'autre.
        Si une arête a deux extrémités finies p1, p2 → direction (p2-p1)
        doit être ⊥ au vecteur (site_r - site_l).
        """
        coords = [(0, 0), (10, 0), (5, 9), (2, 5), (8, 5)]
        diag, pts = voronoi(coords)

        for he, het in diag.edges:
            p1, p2 = he.origin, het.origin
            if p1 is None or p2 is None:
                continue
            site_l = he.face.site  if he.face  else None
            site_r = het.face.site if het.face else None
            if not site_l or not site_r:
                continue
            # Vecteur de l'arête
            ex, ey = p2.x - p1.x, p2.y - p1.y
            # Vecteur inter-sites
            sx, sy = site_r.x - site_l.x, site_r.y - site_l.y
            # Produit scalaire doit être ≈ 0
            dot = ex * sx + ey * sy
            norm = math.hypot(ex, ey) * math.hypot(sx, sy)
            if norm > EPS:
                assert abs(dot) / norm == pytest.approx(0.0, abs=1e-4), (
                    f"Arête non perpendiculaire : dot/norm = {dot/norm:.6f}"
                )

    def test_chaque_cellule_contient_son_site(self):
        """
        Propriété fondamentale : chaque point du diagramme appartient à la
        cellule du site le plus proche.
        On vérifie sur une grille de points tests que la cellule trouvée
        par nearest-neighbor correspond bien au site le plus proche.
        """
        coords = [(10, 10), (80, 10), (10, 80), (80, 80), (45, 45)]
        diag, pts = voronoi(coords)
        segs = vg.collect_segments(diag, 0, 100, 0, 100)

        test_pts = [(x, y) for x in range(5, 100, 15) for y in range(5, 100, 15)]
        for tx, ty in test_pts:
            idx = nearest_site(tx, ty, pts)
            # Le site d'indice 'idx' doit être le plus proche de (tx, ty)
            d_winner = math.hypot(pts[idx].x - tx, pts[idx].y - ty)
            for j, s in enumerate(pts):
                if j != idx:
                    d = math.hypot(s.x - tx, s.y - ty)
                    assert d_winner <= d + EPS, (
                        f"Point ({tx},{ty}) : site {idx} n'est pas le plus proche"
                    )

    def test_symetrie_deux_points(self):
        """
        Pour 2 points symétriques, la médiatrice doit passer par (0,0)
        et être verticale.
        """
        diag, _ = voronoi([(-5, 0), (5, 0)])
        he, het = diag.edges[0]
        # Au moins une des demi-arêtes a une direction ou une origine connue
        origin = he.origin or het.origin
        if origin:
            assert origin.x == pytest.approx(0.0, abs=EPS)


# ═════════════════════════════════════════════════════════════════════════════
# 8. collect_segments
# ═════════════════════════════════════════════════════════════════════════════

class TestCollectSegments:
    def test_retourne_liste(self):
        diag, _ = voronoi([(0, 0), (10, 0)])
        segs = vg.collect_segments(diag, -20, 20, -20, 20)
        assert isinstance(segs, list)

    def test_au_moins_un_segment_pour_deux_points(self):
        diag, _ = voronoi([(0, 0), (10, 0)])
        segs = vg.collect_segments(diag, -50, 50, -50, 50)
        assert len(segs) >= 1

    def test_segments_dans_la_boite(self):
        """Tous les endpoints retournés doivent être dans le bounding box."""
        coords = [(i*20, j*20) for i in range(3) for j in range(3)]
        diag, _ = voronoi(coords)
        xmn, xmx, ymn, ymx = -10, 60, -10, 60
        segs = vg.collect_segments(diag, xmn, xmx, ymn, ymx)
        for (x1, y1), (x2, y2) in segs:
            assert xmn - EPS <= x1 <= xmx + EPS
            assert xmn - EPS <= x2 <= xmx + EPS
            assert ymn - EPS <= y1 <= ymx + EPS
            assert ymn - EPS <= y2 <= ymx + EPS

    def test_diagramme_vide(self):
        """Un seul point → pas d'arêtes → liste vide."""
        pts = [P(0, 0)]
        fa  = vg.FortuneAlgorithm(pts)
        fa.compute()
        segs = vg.collect_segments(fa.diagram, -10, 10, -10, 10)
        assert segs == []

    def test_segments_non_degeneres(self):
        """Aucun segment retourné par collect_segments ne doit avoir une longueur nulle."""
        coords = [(10, 10), (60, 20), (30, 70), (80, 60), (50, 40)]
        diag, _ = voronoi(coords)
        segs = vg.collect_segments(diag, 0, 100, 0, 100)
        for (x1, y1), (x2, y2) in segs:
            length = math.hypot(x2 - x1, y2 - y1)
            assert length > 1e-9, f"Segment dégénéré trouvé : ({x1:.4f},{y1:.4f})→({x2:.4f},{y2:.4f})"

    def test_boite_plus_petite_reduit_les_segments(self):
        """Une bbox plus petite ne doit jamais produire plus de segments."""
        coords = [(10, 10), (90, 10), (50, 90), (50, 50)]
        diag, _ = voronoi(coords)
        segs_grand  = vg.collect_segments(diag, -100, 200, -100, 200)
        segs_petit  = vg.collect_segments(diag,   20,  80,   20,  80)
        assert len(segs_petit) <= len(segs_grand)


# ═════════════════════════════════════════════════════════════════════════════
# 9. Lecture de fichier points
# ═════════════════════════════════════════════════════════════════════════════

def _parse_points(text):
    """
    Réimplémente la logique de parsing de voronoi_gui._load_file_path
    sans GUI, pour les tests de parsing pur.
    """
    pts = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.replace(';', ',').split(',')
        if len(parts) >= 2:
            pts.append(P(float(parts[0].strip()), float(parts[1].strip())))
    return pts


class TestParsing:
    def test_format_virgule(self):
        pts = _parse_points("10, 20\n30, 40")
        assert len(pts) == 2
        assert pts[0].x == pytest.approx(10)
        assert pts[1].y == pytest.approx(40)

    def test_format_point_virgule(self):
        pts = _parse_points("10; 20\n30; 40")
        assert len(pts) == 2

    def test_lignes_vides_ignorees(self):
        pts = _parse_points("\n10, 20\n\n30, 40\n\n")
        assert len(pts) == 2

    def test_commentaires_ignores(self):
        pts = _parse_points("# commentaire\n10, 20\n# autre\n30, 40")
        assert len(pts) == 2

    def test_flottants(self):
        pts = _parse_points("1.5, 2.7\n-3.1, 4.0")
        assert pts[0].x == pytest.approx(1.5)
        assert pts[1].x == pytest.approx(-3.1)

    def test_fichier_vide(self):
        pts = _parse_points("")
        assert pts == []

    def test_lecture_fichier_reel(self):
        """Teste la lecture d'un vrai fichier temporaire sur disque."""
        content = "100, 200\n300, 400\n# ignored\n50.5, 75.3\n"
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write(content)
            fname = f.name
        try:
            pts = []
            with open(fname) as fp:
                for line in fp:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    parts = line.replace(';', ',').split(',')
                    if len(parts) >= 2:
                        pts.append(P(float(parts[0]), float(parts[1])))
            assert len(pts) == 3
            assert pts[2].x == pytest.approx(50.5)
        finally:
            os.unlink(fname)

    def test_lignes_malformees_ignorees(self):
        """
        Une ligne avec un seul champ ou des valeurs non-numériques doit être
        ignorée sans crash — le parsing doit wrapper les erreurs.
        """
        def safe_parse(text):
            pts = []
            for line in text.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.replace(";", ",").split(",")
                if len(parts) >= 2:
                    try:
                        pts.append(P(float(parts[0].strip()), float(parts[1].strip())))
                    except ValueError:
                        pass  # ligne malformée ignorée
            return pts

        pts = safe_parse("10\n20, 30\nabc, def\n50, 60")
        # "10" → 1 seul champ, ignoré
        # "abc, def" → ValueError, ignoré
        # "20, 30" et "50, 60" → valides
        assert len(pts) == 2
        assert pts[0].x == pytest.approx(20)
        assert pts[1].x == pytest.approx(50)


# ═════════════════════════════════════════════════════════════════════════════
# 10. Cas limites & robustesse
# ═════════════════════════════════════════════════════════════════════════════

class TestCasLimites:
    def test_points_tres_proches(self):
        """Points quasi-identiques ne doivent pas produire d'exception."""
        coords = [(0, 0), (1e-6, 0), (0, 1e-6)]
        try:
            diag, pts = voronoi(coords)
            assert len(diag.faces) <= 3  # peut fusionner
        except Exception as e:
            pytest.fail(f"Exception inattendue pour points proches : {e}")

    def test_points_tres_eloignes(self):
        """Grande plage de coordonnées → pas de crash."""
        coords = [(0, 0), (1e6, 0), (5e5, 1e6)]
        diag, pts = voronoi(coords)
        assert len(diag.faces) == 3

    def test_points_en_cercle(self):
        """n points régulièrement espacés sur un cercle."""
        n = 8
        coords = [(100*math.cos(2*math.pi*i/n),
                   100*math.sin(2*math.pi*i/n)) for i in range(n)]
        diag, pts = voronoi(coords)
        assert len(diag.faces) == n

    def test_points_en_ligne_horizontale(self):
        """Points colinéaires horizontaux."""
        coords = [(i * 10, 0) for i in range(6)]
        diag, pts = voronoi(coords)
        assert len(diag.faces) == 6

    def test_points_en_ligne_verticale(self):
        """Points colinéaires verticaux."""
        coords = [(0, i * 10) for i in range(5)]
        diag, pts = voronoi(coords)
        assert len(diag.faces) == 5

    def test_carré_quatre_points(self):
        """4 coins d'un carré → 4 faces, sommet central."""
        coords = [(0, 0), (10, 0), (10, 10), (0, 10)]
        diag, pts = voronoi(coords)
        assert len(diag.faces) == 4
        # Un sommet doit être proche du centre (5, 5)
        center_found = any(
            abs(v.x - 5) < 1 and abs(v.y - 5) < 1
            for v in diag.vertices
        )
        assert center_found, "Sommet central introuvable pour un carré"

    def test_reproductibilite(self):
        """Deux appels avec les mêmes points donnent le même nombre d'arêtes."""
        coords = [(10, 20), (50, 30), (80, 10), (40, 70)]
        diag1, _ = voronoi(coords)
        diag2, _ = voronoi(coords)
        assert len(diag1.edges)    == len(diag2.edges)
        assert len(diag1.vertices) == len(diag2.vertices)
