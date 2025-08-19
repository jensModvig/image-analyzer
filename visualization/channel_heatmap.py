import numpy as np
from visualization.base import VisualizationModule
from gui.heatmap_widgets import create_heatmap_widget
from utils.heatmap_utils import get_colormap_name

class PerChannelHeatmapModule(VisualizationModule):
    def generate_visualizations(self):
        results = []
        
        for i, channel_name in enumerate(self.data_container.channel_names):
            channel = self.data_container.get_channel(i)
            colormap_name = get_colormap_name(channel_name)
            
            dual_axis = channel.dtype == np.uint16
            unit_converter = (lambda x: x / 1000.0) if dual_axis else None
            
            widget = create_heatmap_widget(
                colormap_name=colormap_name,
                min_val=np.min(channel),
                max_val=np.max(channel),
                original_channel_data=channel,
                module_name=self.get_module_name(),
                dual_axis=dual_axis,
                unit_converter=unit_converter
            )
            results.append((f"{channel_name} Heatmap", widget))
        
        return results
    
    def get_module_name(self):
        return "Channel Heatmaps"
    
    @classmethod
    def get_supported_containers(cls):
        from data_containers.image_container import ImageContainer
        return [ImageContainer]