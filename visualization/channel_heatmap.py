import cv2
import numpy as np
from visualization.base import VisualizationModule

class PerChannelHeatmapModule(VisualizationModule):
    def generate_visualizations(self):
        results = []
        
        for i, channel_name in enumerate(self.image_container.channel_names):
            channel = self.image_container.get_channel(i)
            
            normalized = cv2.normalize(channel, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            heatmap = cv2.applyColorMap(normalized, cv2.COLORMAP_JET)
            heatmap_rgb = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
            
            results.append((f"{channel_name} Heatmap", heatmap_rgb))
        
        return results
    
    def get_module_name(self):
        return "Channel Heatmaps"