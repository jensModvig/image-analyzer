import pyvista as pv
import numpy as np
from visualization.base import VisualizationModule
from gui.widget_utils import create_qtinteractor

class PCLUniqueHSVModule(VisualizationModule):
    def generate_visualizations(self):
        if not self.data_container.has_colors or 'original_colors' not in self.data_container.loader_data:
            return []
        
        colors = self.data_container.loader_data['original_colors']
        
        if len(colors.shape) == 1:
            unique_values, indices = np.unique(colors, return_inverse=True)
        else:
            unique_values, indices = np.unique(colors, axis=0, return_inverse=True)
        
        cloud = pv.PolyData(self.data_container.points)
        hsv_colors = self._generate_hsv_colors(len(unique_values))
        cloud['colors'] = hsv_colors[indices]
        
        widget = create_qtinteractor(cloud, self.data_container, module_name=self.get_module_name())
        return [("Unique HSV", widget)]
    
    def _generate_hsv_colors(self, count):
        colors = np.zeros((count, 3), dtype=np.uint8)
        golden_ratio = (1 + 5**0.5) / 2
        
        for i in range(count):
            hue = (i / golden_ratio) % 1.0 * 360
            rgb = self._hsv_to_rgb(hue, 0.8, 0.9)
            colors[i] = [int(c * 255) for c in rgb]
        
        return colors
    
    def _hsv_to_rgb(self, h, s, v):
        h /= 360.0
        i = int(h * 6.0)
        f = (h * 6.0) - i
        p, q, t = v * (1.0 - s), v * (1.0 - s * f), v * (1.0 - s * (1.0 - f))
        return [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)][i % 6]
    
    def get_module_name(self):
        return "PCL Unique HSV"
    
    @classmethod
    def get_supported_containers(cls):
        from data_containers.pcl_container import PCLContainer
        return [PCLContainer]