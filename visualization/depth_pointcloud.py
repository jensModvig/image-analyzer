import pyvista as pv
import numpy as np
from visualization.base import VisualizationModule
from gui.heatmap_widgets import create_vtk_heatmap_widget
from utils.heatmap_utils import get_colormap_name, apply_colormap_to_data
from utils.depth_projection import project_depth_to_pointcloud

class DepthPointCloudModule(VisualizationModule):
    def generate_visualizations(self):
        results = []
        
        for i, channel_name in enumerate(self.data_container.channel_names):
            channel = self.data_container.get_channel(i)
            points, mask = project_depth_to_pointcloud(channel)
            if len(points) == 0:
                raise ValueError(f"No valid points generated for channel {channel_name}")
            
            depth_values = channel[mask]
            colormap_name = get_colormap_name(channel_name)
            
            cloud = pv.PolyData(points)
            cloud['colors'] = apply_colormap_to_data(depth_values, colormap_name)
            
            is_uint16 = channel.dtype == np.uint16
            unit_converter = (lambda x: x / 1000.0) if is_uint16 else None
            
            widget = create_vtk_heatmap_widget(
                cloud=cloud, 
                container=None, 
                original_data=depth_values, 
                module_name=self.get_module_name(),
                min_val=np.min(depth_values), 
                max_val=np.max(depth_values), 
                colormap_name=colormap_name, 
                dual_axis=is_uint16, 
                unit_converter=unit_converter
            )
            results.append((f"{channel_name} Depth PCL", widget))
        
        return results
    
    def get_module_name(self):
        return "Depth Point Clouds"
    
    @classmethod
    def get_supported_containers(cls):
        from data_containers.image_container import ImageContainer
        return [ImageContainer]