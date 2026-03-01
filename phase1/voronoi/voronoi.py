import tkinter
from tkinter import filedialog
from pathlib import Path
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from math import sqrt


class Point:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def __add__(self, other):
        return Point(self.x+other.x, self.y+other.y)
    def __sub__(self, other):
        return Point(self.x-other.x, self.y-other.y)
    
    def __mul__(self, scale:float):
        return Point(self.x * scale, self.y * scale)
    def __truediv__(self, divisor:float):
        return Point(self.x / divisor, self.y / divisor)


def load_file():
    """Permet de load un fichier du système"""
    global current_file_imported
    filename = filedialog.askopenfilename()
    if (filename):
        with open(filename) as fichier:
            current_file_imported = fichier.readlines()
            # print(current_file_imported)

    else: 
        print("No file")
        current_file_imported = None
    return current_file_imported

# Partie interface graphique tkinter
window = tkinter.Tk()
window.title("Voronoi")
window.geometry("1024x720")



current_file_imported = ""






def generate_voronoi(file = None):
    """Génère l'affichage de voronoi à partir d'une liste de points dans un fichier"""
    global plot1, canvas
    if (file is None or len(file) == 0):
        return
    
    plot1.clear()

    tab_points = []
    for lines in file:
        """
        on récupère les points aléatoire du fichier
        """
        values = lines.replace("\n","").split(",")
        tab_points.append(Point(float(values[0]), float(values[1])))

    max_points_x = 0
    max_points_y = 0
    for point in tab_points:
        """
        pour savoir le plus grand x et y de tous les points pour la fenêtre
        """
        if point.x > max_points_x: 
            max_points_x = point.x
        if point.y > max_points_y: 
            max_points_y = point.y

    max_points_x += 1
    max_points_y += 1
    resolution = 500
    grille = [[0 for k in range(resolution)] for k in range(resolution)] #[[0,0,...,0],[0,..,0],...]

    for ligne in range(resolution):
        for colonne in range(resolution):
            """
            calcule de Voronoi, methode de la grille
            """
            x_pixel = (colonne / resolution)*max_points_x #produit en croix pour pixel en coordonnées
            y_pixel = (ligne / resolution)*max_points_y
            distance_min = 100000 
            index_point_proche = 0
            
            for i in range(len(tab_points)):
                """
                on teste tout les points les plus proche de chaque pixel dans le tab_points
                """
                point = tab_points[i]  
                distance_x = x_pixel - point.x
                distance_y = y_pixel - point.y
                distance_final = sqrt(distance_x*distance_x + distance_y*distance_y) #formule distance entre 2 points
                
                if distance_final < distance_min:
                    distance_min = distance_final
                    index_point_proche = i
            
            grille[ligne][colonne] = index_point_proche

    #plt.figure(figsize=(5,8))
    plot1.imshow(grille, extent=(0, max_points_x, 0, max_points_y), origin='lower') #affiche frontière voronoie en coloriant à chaque fois que le x,y de chaque pixel de la grille change
    plot1.scatter([point.x for point in tab_points], [point.y for point in tab_points])

    canvas.draw()
    canvas.get_tk_widget().pack()

    # plot1.savefig("voronoi.png", dpi=300)





load_button = tkinter.Button(master=window, text="Ouvrir un fichier", command=load_file)
load_button.pack()

generate_button = tkinter.Button(master=window, text="Générer voronoi", command=lambda: generate_voronoi(current_file_imported))
generate_button.pack()

fig = Figure(figsize=(5, 5), dpi=100)
plot1 = fig.add_subplot(111)

canvas = FigureCanvasTkAgg(fig, master=window)

toolbar = NavigationToolbar2Tk(canvas,
                                window)
toolbar.update()


    
window.mainloop()
