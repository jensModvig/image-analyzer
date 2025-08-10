import pyvista as pv
import numpy as np
from visualization.base import VisualizationModule

class PCLRGBModule(VisualizationModule):
    def generate_visualizations(self):
        cloud = pv.PolyData(self.data_container.points)
        
        plotter = pv.Plotter()
        
        if self.data_container.has_colors:
            colors = (self.data_container.colors * 255).astype(np.uint8)
            cloud['colors'] = colors
            plotter.add_mesh(cloud, scalars='colors', rgb=True, point_size=2.0)
        else:
            plotter.add_mesh(cloud, color='lightgray', point_size=2.0)
        
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
        
        return [("PCL RGB", plotter)]
    
    def get_module_name(self):
        return "PCL RGB"
    
    @classmethod
    def get_supported_containers(cls):
        from data_containers.pcl_container import PCLContainer
        return [PCLContainer]