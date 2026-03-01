"""
Générateur de diagramme de Voronoï — Interface Graphique Interactive
Algorithme : Fortune's Sweep Line (O(n log n))
GUI      : Tkinter + Matplotlib embarqué

Contrôles :
  • Clic gauche sur le canvas  → ajouter un point
  • Clic droit sur un point    → supprimer ce point
  • Bouton "Charger fichier"   → importer points depuis un .txt
  • Bouton "Effacer"           → tout réinitialiser
  • Bouton "Exporter PNG"      → sauvegarder l'image
  • Slider "Opacité cellules"  → ajuster la transparence des couleurs
"""

import sys, math, heapq, os, random, tkinter as tk
from tkinter import filedialog, messagebox, ttk

import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.collections import LineCollection


# ═══════════════════════════════════════════════════════════════════════════════
#   ALGORITHME DE FORTUNE
# ═══════════════════════════════════════════════════════════════════════════════

EPS = 1e-9


class Point:
    __slots__ = ['x', 'y']
    def __init__(self, x, y): self.x = float(x); self.y = float(y)


class HalfEdge:
    __slots__ = ['origin','twin','face','direction']
    def __init__(self):
        self.origin = self.twin = self.face = self.direction = None


class Face:
    __slots__ = ['site']
    def __init__(self, site): self.site = site


class VoronoiDiagram:
    def __init__(self):
        self.vertices = []
        self.edges    = []   # liste de (he, het)
        self.faces    = []


class Arc:
    __slots__ = ['site','prev','next','event','s0','s1']
    def __init__(self, s):
        self.site = s
        self.prev = self.next = self.event = self.s0 = self.s1 = None


class Event:
    __slots__ = ['x','point','arc','valid']
    def __init__(self, x, pt, arc=None):
        self.x = x; self.point = pt; self.arc = arc; self.valid = True
    def __lt__(self, o):
        return self.x < o.x if abs(self.x - o.x) > EPS else self.point.y < o.point.y


def _par_inter(p1, p2, sx):
    d1, d2 = 2*(p1.x - sx), 2*(p2.x - sx)
    if abs(d1) < EPS: return p1.y
    if abs(d2) < EPS: return p2.y
    if abs(p1.x - p2.x) < EPS: return (p1.y + p2.y) / 2
    a = 1/d1 - 1/d2
    b = -2*(p1.y/d1 - p2.y/d2)
    c = (p1.y**2 + p1.x**2 - sx**2)/d1 - (p2.y**2 + p2.x**2 - sx**2)/d2
    disc = max(0.0, b*b - 4*a*c)
    sq = math.sqrt(disc)
    y1, y2 = (-b+sq)/(2*a), (-b-sq)/(2*a)
    return y1 if p1.x < p2.x else y2


def circumcenter(a, b, c):
    ax, ay = a.x - c.x, a.y - c.y
    bx, by = b.x - c.x, b.y - c.y
    D = 2*(ax*by - ay*bx)
    if abs(D) < EPS: return None
    ux = (by*(ax*ax+ay*ay) - ay*(bx*bx+by*by)) / D + c.x
    uy = (ax*(bx*bx+by*by) - bx*(ax*ax+ay*ay)) / D + c.y
    return Point(ux, uy)


class FortuneAlgorithm:
    def __init__(self, points):
        self.sites   = [Point(p.x, p.y) for p in points]
        self.diagram = VoronoiDiagram()
        self.queue   = []
        self.arcs    = None

    def _face_of(self, site):
        for f in self.diagram.faces:
            if f.site is site: return f
        f = Face(site); self.diagram.faces.append(f); return f

    def _new_edge(self, sl, sr):
        he, het = HalfEdge(), HalfEdge()
        he.twin = het; het.twin = he
        he.face = self._face_of(sl); het.face = self._face_of(sr)
        self.diagram.edges.append((he, het))
        return he, het

    def compute(self):
        for s in self.sites:
            heapq.heappush(self.queue, Event(s.x, s))
        while self.queue:
            ev = heapq.heappop(self.queue)
            if not ev.valid: continue
            if ev.arc is None: self._site(ev)
            else:              self._circle(ev)
        self._finish()

    def _site(self, ev):
        site = ev.point; sx = site.x
        if self.arcs is None:
            self.arcs = Arc(site); return
        arc = self.arcs
        while arc.next:
            if site.y < _par_inter(arc.site, arc.next.site, sx) - EPS: break
            arc = arc.next
        if arc.event: arc.event.valid = False; arc.event = None
        dup = Arc(arc.site); na = Arc(site)
        dup.next = arc.next; dup.prev = na
        na.next = dup; na.prev = arc
        if arc.next: arc.next.prev = dup
        arc.next = na
        he, het = self._new_edge(arc.site, site)
        arc.s1 = he; na.s0 = het
        he2, het2 = self._new_edge(site, arc.site)
        na.s1 = he2; dup.s0 = het2
        self._check(arc); self._check(dup)

    def _circle(self, ev):
        arc = ev.arc; v = ev.point
        self.diagram.vertices.append(v)
        if arc.prev and arc.prev.event: arc.prev.event.valid = False; arc.prev.event = None
        if arc.next and arc.next.event: arc.next.event.valid = False; arc.next.event = None
        if arc.s0: arc.s0.origin = v
        if arc.s1: arc.s1.origin = v
        if arc.prev and arc.prev.s1: arc.prev.s1.origin = v
        if arc.next and arc.next.s0: arc.next.s0.origin = v
        if arc.prev and arc.next:
            he, het = self._new_edge(arc.prev.site, arc.next.site)
            he.origin = het.origin = v
            arc.prev.s1 = he; arc.next.s0 = het
        if arc.prev: arc.prev.next = arc.next
        if arc.next: arc.next.prev = arc.prev
        if arc.prev: self._check(arc.prev)
        if arc.next: self._check(arc.next)

    def _check(self, arc):
        if not arc.prev or not arc.next: return
        a, b, c = arc.prev.site, arc.site, arc.next.site
        if (b.x-a.x)*(c.y-a.y) - (b.y-a.y)*(c.x-a.x) >= 0: return
        cc = circumcenter(a, b, c)
        if cc is None: return
        r  = math.hypot(cc.x - b.x, cc.y - b.y)
        ev = Event(cc.x + r, cc, arc)
        arc.event = ev
        heapq.heappush(self.queue, ev)

    def _finish(self):
        arc = self.arcs
        while arc and arc.next:
            if arc.s1 and arc.s1.origin is None:
                mx = (arc.site.x + arc.next.site.x) / 2
                my = (arc.site.y + arc.next.site.y) / 2
                arc.s1.direction = Point(-(arc.next.site.y - arc.site.y),
                                          (arc.next.site.x - arc.site.x))
                arc.s1.origin    = Point(mx, my)
            arc = arc.next


def clip_seg(p1, p2, xmn, xmx, ymn, ymx):
    def code(p):
        c = 0
        if p[0] < xmn: c |= 1
        if p[0] > xmx: c |= 2
        if p[1] < ymn: c |= 4
        if p[1] > ymx: c |= 8
        return c
    x1,y1,x2,y2 = p1[0],p1[1],p2[0],p2[1]
    for _ in range(20):
        c1,c2 = code((x1,y1)), code((x2,y2))
        if not (c1|c2): return (x1,y1),(x2,y2)
        if c1&c2:       return None
        c = c1 or c2
        if   c&8: x=x1+(x2-x1)*(ymx-y1)/(y2-y1+EPS); y=ymx
        elif c&4: x=x1+(x2-x1)*(ymn-y1)/(y2-y1+EPS); y=ymn
        elif c&2: y=y1+(y2-y1)*(xmx-x1)/(x2-x1+EPS); x=xmx
        else:     y=y1+(y2-y1)*(xmn-x1)/(x2-x1+EPS); x=xmn
        if c==c1: x1,y1=x,y
        else:     x2,y2=x,y
    return None


def collect_segments(diagram, xmn, xmx, ymn, ymx, far=1e5):
    segs = []
    for he, het in diagram.edges:
        p1, p2 = he.origin, het.origin
        if p1 is None and p2 is None: continue
        # Ignorer les arêtes dégénérées (même sommet aux deux bouts)
        if p1 is not None and p2 is not None:
            if abs(p1.x - p2.x) < 1e-12 and abs(p1.y - p2.y) < 1e-12:
                continue
        if p1 is None or p2 is None:
            edge   = he if p2 is None else het
            origin = edge.twin.origin if edge.origin is None else edge.origin
            if origin is None: continue
            d = edge.direction or edge.twin.direction
            if d is None: continue
            n = math.hypot(d.x, d.y)
            if n < EPS: continue
            p1 = origin
            p2 = Point(origin.x + d.x/n*far, origin.y + d.y/n*far)
        r = clip_seg((p1.x,p1.y),(p2.x,p2.y), xmn,xmx,ymn,ymx)
        if r:
            (rx1,ry1),(rx2,ry2) = r
            if math.hypot(rx2-rx1, ry2-ry1) > 1e-9:
                segs.append(r)
    return segs


def compute_voronoi(points):
    fa = FortuneAlgorithm(points)
    fa.compute()
    return fa.diagram


# ═══════════════════════════════════════════════════════════════════════════════
#   INTERFACE GRAPHIQUE
# ═══════════════════════════════════════════════════════════════════════════════

DARK_BG   = "#1a1a2e"
DARK_PANEL= "#16213e"
ACCENT    = "#0f3460"
BTN_FG    = "#e0e0ff"
BTN_HOVER = "#e94560"

PALETTE_SEED = 42


class VoronoiApp:
    def __init__(self, root):
        self.root   = root
        self.root.title("Diagramme de Voronoï — Fortune's Algorithm")
        self.root.configure(bg=DARK_BG)
        self.root.geometry("1100x750")

        self.points  = []
        self.opacity = tk.DoubleVar(value=0.55)
        self._colors = {}          # cache couleurs par index
        self._rng    = random.Random(PALETTE_SEED)

        self._build_ui()
        self._draw()

    # ── Construction de l'UI ─────────────────────────────────────────────────

    def _build_ui(self):
        # Panneau latéral gauche
        panel = tk.Frame(self.root, bg=DARK_PANEL, width=200)
        panel.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        panel.pack_propagate(False)

        tk.Label(panel, text="🔷 Voronoï", bg=DARK_PANEL, fg=BTN_FG,
                 font=("Helvetica", 16, "bold")).pack(pady=(20, 4))
        tk.Label(panel, text="Fortune's Sweep Line", bg=DARK_PANEL,
                 fg="#7788aa", font=("Helvetica", 9)).pack(pady=(0, 20))

        sep = tk.Frame(panel, bg="#2a2a4a", height=1)
        sep.pack(fill=tk.X, padx=16, pady=4)

        # Info points
        self.lbl_count = tk.Label(panel, text="Points : 0", bg=DARK_PANEL,
                                   fg=BTN_FG, font=("Helvetica", 11))
        self.lbl_count.pack(pady=8)

        # Instructions
        info = (
            "🖱 Clic gauche\n→ Ajouter un point\n\n"
            "🖱 Clic droit\n→ Supprimer un point\n\n"
            "🖱 Molette\n→ Zoom\n"
        )
        tk.Label(panel, text=info, bg=DARK_PANEL, fg="#9999bb",
                 font=("Courier", 9), justify=tk.LEFT).pack(padx=16, pady=10)

        sep2 = tk.Frame(panel, bg="#2a2a4a", height=1)
        sep2.pack(fill=tk.X, padx=16, pady=4)

        # Slider opacité
        tk.Label(panel, text="Opacité des cellules", bg=DARK_PANEL,
                 fg=BTN_FG, font=("Helvetica", 10)).pack(pady=(12,2))
        sl = ttk.Scale(panel, from_=0, to=1, variable=self.opacity,
                       orient=tk.HORIZONTAL, command=lambda _: self._draw())
        sl.pack(fill=tk.X, padx=20, pady=4)

        # Boutons
        btns = [
            ("📂  Charger fichier",  self._load_file),
            ("🔀  Points aléatoires", self._random_points),
            ("🗑  Effacer tout",      self._clear),
            ("💾  Exporter PNG",      self._export),
        ]
        for label, cmd in btns:
            b = tk.Button(panel, text=label, command=cmd,
                          bg=ACCENT, fg=BTN_FG, relief=tk.FLAT,
                          font=("Helvetica", 10), cursor="hand2",
                          activebackground=BTN_HOVER, activeforeground="white",
                          padx=8, pady=6)
            b.pack(fill=tk.X, padx=16, pady=5)

        # Canvas matplotlib
        canvas_frame = tk.Frame(self.root, bg=DARK_BG)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(8, 7), facecolor=DARK_BG)
        self.fig.subplots_adjust(left=0.05, right=0.98, top=0.95, bottom=0.06)
        self.ax.set_facecolor(DARK_BG)

        self.canvas = FigureCanvasTkAgg(self.fig, master=canvas_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar_frame = tk.Frame(canvas_frame, bg=DARK_PANEL)
        toolbar_frame.pack(fill=tk.X)
        tb = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        tb.configure(bg=DARK_PANEL)
        tb.update()

        self.canvas.mpl_connect("button_press_event", self._on_click)

    # ── Couleurs persistantes ─────────────────────────────────────────────────

    def _color_for(self, idx):
        if idx not in self._colors:
            h = self._rng.random()
            # HSV → RGB (pastel)
            import colorsys
            r, g, b = colorsys.hsv_to_rgb(h, 0.55, 0.90)
            self._colors[idx] = (r, g, b)
        return self._colors[idx]

    # ── Dessin ────────────────────────────────────────────────────────────────

    def _draw(self):
        ax = self.ax
        ax.cla()
        ax.set_facecolor(DARK_BG)

        pts = self.points
        n   = len(pts)
        self.lbl_count.config(text=f"Points : {n}")

        if n == 0:
            ax.text(0.5, 0.5, "Cliquez pour ajouter des points",
                    ha='center', va='center', color='#4455aa',
                    fontsize=14, transform=ax.transAxes)
            ax.set_xlim(0, 500); ax.set_ylim(0, 500)
            self._style_ax()
            self.canvas.draw()
            return

        xs = [p.x for p in pts]; ys = [p.y for p in pts]
        span = max(max(xs)-min(xs), max(ys)-min(ys), 50)
        mg   = span * 0.18 + 20
        xmn, xmx = min(xs)-mg, max(xs)+mg
        ymn, ymx = min(ys)-mg, max(ys)+mg

        ax.set_xlim(xmn, xmx); ax.set_ylim(ymn, ymx)

        if n == 1:
            ax.scatter(xs, ys, c='white', s=80, zorder=5)
            self._style_ax(); self.canvas.draw(); return

        # Calcul Voronoï
        # Coloriage par NN (résolution adaptée)
        res = 500
        xi = np.linspace(xmn, xmx, res)
        yi = np.linspace(ymn, ymx, res)
        gx, gy = np.meshgrid(xi, yi)
        px = np.array(xs); py = np.array(ys)
        dist = (gx[:,:,None]-px)**2 + (gy[:,:,None]-py)**2
        ids  = np.argmin(dist, axis=2)

        palette = np.array([self._color_for(i) for i in range(n)])
        img = palette[ids]
        ax.imshow(img, extent=[xmn, xmx, ymn, ymx], origin='lower',
                  interpolation='nearest', alpha=self.opacity.get(),
                  aspect='auto', zorder=1)

        # Points
        ax.scatter(xs, ys, c='white', s=70, zorder=5,
                   edgecolors=DARK_BG, linewidths=1.5)

        # Labels
        for i, p in enumerate(pts):
            ax.annotate(f" {i+1}", (p.x, p.y), color='#ddddff',
                        fontsize=8, zorder=6,
                        xytext=(4, 4), textcoords='offset points')

        self._style_ax()
        self.canvas.draw()

    def _style_ax(self):
        ax = self.ax
        ax.set_title("Diagramme de Voronoï", color='#aabbff',
                     fontsize=13, pad=10)
        ax.tick_params(colors='#445566')
        for sp in ax.spines.values():
            sp.set_edgecolor('#334455')

    # ── Événements souris ─────────────────────────────────────────────────────

    def _on_click(self, event):
        if event.inaxes != self.ax: return
        if event.button == 1:          # Gauche → ajouter
            self.points.append(Point(event.xdata, event.ydata))
            self._draw()
        elif event.button == 3:        # Droit → supprimer le plus proche
            if not self.points: return
            dists = [(math.hypot(p.x - event.xdata, p.y - event.ydata), i)
                     for i, p in enumerate(self.points)]
            _, idx = min(dists)
            # seuil de sélection en coords données
            xmn, xmx = self.ax.get_xlim()
            threshold = (xmx - xmn) * 0.04
            if dists[idx][0] < threshold:
                self.points.pop(idx)
                self._draw()

    # ── Actions boutons ───────────────────────────────────────────────────────

    def _load_file(self):
        path = filedialog.askopenfilename(
            title="Choisir un fichier de points",
            filetypes=[("Fichiers texte", "*.txt *.csv"), ("Tous", "*.*")]
        )
        if not path: return
        pts = []
        try:
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'): continue
                    parts = line.replace(';', ',').split(',')
                    if len(parts) >= 2:
                        pts.append(Point(float(parts[0]), float(parts[1])))
        except Exception as e:
            messagebox.showerror("Erreur", f"Lecture impossible :\n{e}")
            return
        if pts:
            self.points = pts
            self._colors.clear()
            self._draw()
        else:
            messagebox.showwarning("Attention", "Aucun point valide trouvé.")

    def _random_points(self):
        n = random.randint(8, 20)
        self.points = [Point(random.uniform(50, 450), random.uniform(50, 450))
                       for _ in range(n)]
        self._colors.clear()
        self._draw()

    def _clear(self):
        self.points = []
        self._colors.clear()
        self._draw()

    def _export(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("SVG", "*.svg"), ("PDF", "*.pdf")]
        )
        if path:
            self.fig.savefig(path, dpi=150, bbox_inches='tight')
            messagebox.showinfo("Exporté", f"Image sauvegardée :\n{path}")

    def _load_file_path(self, path):
        """Charge directement depuis un chemin (utilisé en argument CLI)."""
        pts = []
        try:
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'): continue
                    parts = line.replace(';', ',').split(',')
                    if len(parts) >= 2:
                        pts.append(Point(float(parts[0]), float(parts[1])))
        except Exception as e:
            messagebox.showerror("Erreur", f"Lecture impossible :\n{e}")
            return
        if pts:
            self.points = pts
            self._colors.clear()
            self._draw()


# ═══════════════════════════════════════════════════════════════════════════════
#   POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    root = tk.Tk()
    app  = VoronoiApp(root)

    # Charger un fichier passé en argument si présent
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        app._load_file_path(sys.argv[1])

    root.mainloop()
