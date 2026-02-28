class DataProvider:
    @staticmethod
    def load_points(filename):
        pts = []
        try:
            with open(filename, 'r') as f:
                for line in f:
                    parts = line.replace(',', ' ').split()
                    if len(parts) >= 2:
                        pts.append((float(parts[0]), float(parts[1])))
        except (FileNotFoundError, ValueError) as e:
            print(f"Erreur lors de la lecture : {e}")
        return pts