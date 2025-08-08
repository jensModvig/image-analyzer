import cv2
import numpy as np
from visualization.base import VisualizationModule

class PerChannelHeatmapModule(VisualizationModule):
    def generate_visualizations(self):
        results = []
        
        for i, channel_name in enumerate(self.image_container.channel_names):
            channel = self.image_container.get_channel(i)
            colormap = self._get_colormap_for_channel(channel_name)
            
            normalized = cv2.normalize(channel, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            heatmap = cv2.applyColorMap(normalized, colormap)
            heatmap_rgb = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
            
            colorbar = self._create_colorbar(channel, colormap)
            spacer = np.full((heatmap_rgb.shape[0], 10, 3), 255, dtype=np.uint8)
            combined = np.hstack([heatmap_rgb, spacer, colorbar])
            
            results.append((f"{channel_name} Heatmap", combined))
        
        return results
    
    def _get_colormap_for_channel(self, channel_name):
        colormap_mapping = {
            'R': cv2.COLORMAP_PLASMA,
            'G': cv2.COLORMAP_VIRIDIS,
            'B': cv2.COLORMAP_CIVIDIS
        }
        return colormap_mapping.get(channel_name, cv2.COLORMAP_JET)
    
    def _create_colorbar(self, channel, colormap):
        ch_min = np.min(channel)
        ch_max = np.max(channel)
        
        gradient = np.linspace(255, 0, 256, dtype=np.uint8).reshape(256, 1)
        colorbar = cv2.applyColorMap(gradient, colormap)
        colorbar = cv2.cvtColor(colorbar, cv2.COLOR_BGR2RGB)
        colorbar = np.repeat(colorbar, 30, axis=1)
        colorbar = cv2.resize(colorbar, (30, channel.shape[0]))
        
        cv2.putText(colorbar, f'{ch_max:.1f}', (2, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
        cv2.putText(colorbar, f'{ch_min:.1f}', (2, channel.shape[0]-5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
        
        return colorbar
    
    def get_module_name(self):
        return "Channel Heatmaps"