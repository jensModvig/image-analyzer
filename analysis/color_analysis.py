import numpy as np
from analysis.base import AnalysisModule

class ColorAnalysisModule(AnalysisModule):
    def extract_properties(self):
        properties = []
        
        if self.data_container.channels == 1:
            unique_colors = len(np.unique(self.data_container.original))
            properties.append(("Unique Values", unique_colors, False))
        else:
            reshaped = self.data_container.original.reshape(-1, self.data_container.channels)
            unique_colors = len(np.unique(reshaped, axis=0))
            properties.append(("Unique Colors", unique_colors, False))
            
            dominant_colors = self._get_dominant_colors(reshaped)
            properties.append(("Dominant Colors", dominant_colors, True))
        
        return properties
    
    def _get_dominant_colors(self, reshaped_image, k=5):
        try:
            from sklearn.cluster import KMeans
            
            kmeans = KMeans(n_clusters=min(k, len(np.unique(reshaped_image, axis=0))), 
                          random_state=42, n_init=10)
            kmeans.fit(reshaped_image)
            
            colors = kmeans.cluster_centers_.astype(int)
            return [tuple(color) for color in colors]
        except ImportError:
            unique_vals = np.unique(reshaped_image, axis=0)
            return [tuple(color) for color in unique_vals[:5]]
    
    def get_module_name(self):
        return "Color Analysis"
    
    @classmethod
    def get_supported_containers(cls):
        from data_containers.image_container import ImageContainer
        return [ImageContainer]