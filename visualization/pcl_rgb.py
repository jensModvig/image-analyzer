import pyvista as pv
import numpy as np
from visualization.base import VisualizationModule
from gui.widget_utils import create_qtinteractor

class PCLRGBModule(VisualizationModule):
    def generate_visualizations(self):
        cloud = pv.PolyData(self.data_container.points)
        
        if self.data_container.has_colors:
            colors = np.asarray(self.data_container.point_cloud.colors)
            cloud['colors'] = (colors * 255).astype(np.uint8)
        
        widget = create_qtinteractor(cloud, self.data_container)
        return [("PCL RGB", widget)]
    
    def get_module_name(self):
        return "PCL RGB"
    
    @classmethod
    def get_supported_containers(cls):
        from data_containers.pcl_container import PCLContainer
        return [PCLContainer]