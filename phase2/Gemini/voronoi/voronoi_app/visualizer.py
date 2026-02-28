import matplotlib.pyplot as plt

class VoronoiVisualizer:
    @staticmethod
    def plot(points, cells, x_max=30, y_max=30):
        plt.figure(figsize=(8, 8))
        for cell in cells:
            if cell:
                draw_poly = cell + [cell[0]]
                plt.plot([p[0] for p in draw_poly], [p[1] for p in draw_poly], 'k-', lw=1.5)
        
        plt.scatter([p[0] for p in points], [p[1] for p in points], c='blue', zorder=3)
        plt.xlim(0, x_max)
        plt.ylim(0, y_max)
        plt.gca().set_aspect('equal')
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.savefig("../img/voronoi.png", dpi=300)

        plt.show()
