import pyvista as pv
import numpy as np
from visualization.base import VisualizationModule

class PCLBlackModule(VisualizationModule):
    def generate_visualizations(self):
        cloud = pv.PolyData(self.data_container.points)
        
        plotter = pv.Plotter()
        plotter.add_mesh(cloud, color='black', point_size=2.0)
        
        state = self.data_container.get_camera_state()
        plotter.camera.position = state['position']
        plotter.camera.focal_point = state['focal_point']
        plotter.camera.up = state['up']
        
        def update_camera():
            self.data_container.set_camera_state({
                'position': np.array(plotter.camera.position),
                'focal_point': np.array(plotter.camera.focal_point),
                'up': np.array(plotter.camera.up)
            })
        
        plotter.iren.add_observer('EndInteractionEvent', lambda obj, event: update_camera())
        
        return [("PCL Black", plotter)]
    
    def get_module_name(self):
        return "PCL Black"
    
    @classmethod
    def get_supported_containers(cls):
        from data_containers.pcl_container import PCLContainer
        return [PCLContainer]