import cv2
import numpy as np
from visualization.base import VisualizationModule
from gui.widget_utils import create_heatmap_widget, get_colormap_name, get_opencv_colormap

class PerChannelHeatmapModule(VisualizationModule):
    def generate_visualizations(self):
        results = []
        
        for i, channel_name in enumerate(self.data_container.channel_names):
            channel = self.data_container.get_channel(i)
            colormap_name = get_colormap_name(channel_name)
            colormap = get_opencv_colormap(colormap_name)
            
            normalized = cv2.normalize(channel, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            heatmap = cv2.applyColorMap(normalized, colormap)
            heatmap_rgb = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
            
            widget = create_heatmap_widget(heatmap_rgb, colormap_name, np.min(channel), np.max(channel))
            results.append((f"{channel_name} Heatmap", widget))
        
        return results
    
    def get_module_name(self):
        return "Channel Heatmaps"
    
    @classmethod
    def get_supported_containers(cls):
        from data_containers.image_container import ImageContainer
        return [ImageContainer]