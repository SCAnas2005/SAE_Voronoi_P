from geometry import VoronoiClipper
from data_io import DataProvider
from visualizer import VoronoiVisualizer

def main():
    list_of_points = DataProvider.load_points("../data/voronoi.txt")
    if not list_of_points:
        return

    # On utilise une boîte de calcul large pour simuler l'infini
    clipper = VoronoiClipper(bounding_box=(-200, -200, 200, 200))
    voronoi_cells_collection = []
    
    for current_index, target_point in enumerate(list_of_points):
        # On commence avec une cellule géante
        cell_polygon = clipper.generate_initial_bounding_cell()
        
        for neighbor_index, neighbor_point in enumerate(list_of_points):
            if current_index == neighbor_index:
                continue
            
            # On découpe la cellule actuelle par rapport à chaque voisin
            cell_polygon = clipper.clip_cell_by_neighbor(cell_polygon, target_point, neighbor_point)
            
        voronoi_cells_collection.append(cell_polygon)

    # Rendu final avec le cadrage 30x30 demandé
    VoronoiVisualizer.plot(list_of_points, voronoi_cells_collection, x_max=30, y_max=30)
    

if __name__ == "__main__":
    main()