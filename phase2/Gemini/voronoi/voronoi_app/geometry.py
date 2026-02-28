class GeometryUtils:
    @staticmethod
    def calculate_squared_distance(point_a, point_b):
        """Calcule la distance au carré entre deux coordonnées."""
        return (point_a[0] - point_b[0])**2 + (point_a[1] - point_b[1])**2

    @staticmethod
    def find_bisector_intersection(segment_start, segment_end, target_point, neighbor_point):
        """
        Trouve l'intersection entre un segment de cellule et la médiatrice 
        séparant le point cible de son voisin.
        """
        # Calcul du milieu de la médiatrice
        midpoint_x = (target_point[0] + neighbor_point[0]) / 2
        midpoint_y = (target_point[1] + neighbor_point[1]) / 2
        
        # Vecteur normal à la médiatrice
        normal_x = neighbor_point[0] - target_point[0]
        normal_y = neighbor_point[1] - target_point[1]
        
        # Vecteur du segment de la cellule
        segment_vector_x = segment_end[0] - segment_start[0]
        segment_vector_y = segment_end[1] - segment_start[1]
        
        denominator = normal_x * segment_vector_x + normal_y * segment_vector_y
        
        if abs(denominator) < 1e-10: 
            return None
        
        # Calcul du paramètre t pour trouver le point d'intersection précis
        t_parameter = (normal_x * (midpoint_x - segment_start[0]) + 
                       normal_y * (midpoint_y - segment_start[1])) / denominator
        
        intersection_x = segment_start[0] + t_parameter * segment_vector_x
        intersection_y = segment_start[1] + t_parameter * segment_vector_y
        
        return (intersection_x, intersection_y)

class VoronoiClipper:
    def __init__(self, bounding_box=(-100, -100, 100, 100)):
        self.bounding_box = bounding_box

    def generate_initial_bounding_cell(self):
        min_x, min_y, max_x, max_y = self.bounding_box
        return [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]

    def clip_cell_by_neighbor(self, current_polygon, target_point, neighbor_point):
        """Applique le clipping de Sutherland-Hodgman sur un polygone."""
        new_clipped_polygon = []
        
        for i in range(len(current_polygon)):
            vertex_start = current_polygon[i]
            vertex_end = current_polygon[(i + 1) % len(current_polygon)]
            
            # Un point est "dedans" s'il est plus proche du point cible que du voisin
            is_start_inside = (GeometryUtils.calculate_squared_distance(vertex_start, target_point) < 
                               GeometryUtils.calculate_squared_distance(vertex_start, neighbor_point))
            is_end_inside = (GeometryUtils.calculate_squared_distance(vertex_end, target_point) < 
                             GeometryUtils.calculate_squared_distance(vertex_end, neighbor_point))

            if is_start_inside and is_end_inside:
                new_clipped_polygon.append(vertex_end)
            elif is_start_inside and not is_end_inside:
                intersection = GeometryUtils.find_bisector_intersection(vertex_start, vertex_end, target_point, neighbor_point)
                if intersection: 
                    new_clipped_polygon.append(intersection)
            elif not is_start_inside and is_end_inside:
                intersection = GeometryUtils.find_bisector_intersection(vertex_start, vertex_end, target_point, neighbor_point)
                if intersection: 
                    new_clipped_polygon.append(intersection)
                    new_clipped_polygon.append(vertex_end)
                    
        return new_clipped_polygon