import pyvista as pv
import numpy as np
from visualization.base import VisualizationModule
from gui.heatmap_widgets import create_vtk_heatmap_widget
from utils.heatmap_utils import get_colormap_name, apply_colormap_to_data

class PCLChannelHeatmapModule(VisualizationModule):
    def generate_visualizations(self):
        results = []
        
        if not self.data_container.has_colors:
            return results
        
        for i, channel_name in enumerate(self.data_container.channel_names):
            channel = self.data_container.get_color_channel(i)
            colormap_name = get_colormap_name(channel_name)
            
            cloud = pv.PolyData(self.data_container.points)
            cloud['colors'] = apply_colormap_to_data(channel, colormap_name)
            
            dual_axis = channel.dtype == np.uint16
            unit_converter = (lambda x: x / 1000.0) if dual_axis else None
            
            widget = create_vtk_heatmap_widget(
                cloud=cloud, 
                container=self.data_container, 
                original_data=channel, 
                module_name=self.get_module_name(),
                min_val=np.min(channel), 
                max_val=np.max(channel), 
                colormap_name=colormap_name, 
                dual_axis=dual_axis, 
                unit_converter=unit_converter
            )
            results.append((f"{channel_name} Heatmap", widget))
        
        return results
    
    def get_module_name(self):
        return "PCL Channel Heatmaps"
    
    @classmethod
    def get_supported_containers(cls):
        from data_containers.pcl_container import PCLContainer
        return [PCLContainer]