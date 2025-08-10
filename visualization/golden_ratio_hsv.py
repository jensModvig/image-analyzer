import cv2
import numpy as np
from visualization.base import VisualizationModule

class GoldenRatioHSVModule(VisualizationModule):
    def generate_visualizations(self):
        results = []
        
        if self.image_container.channels == 1:
            unique_vals = np.unique(self.image_container.original)
            if len(unique_vals) <= 500:
                results.append(("Golden Ratio HSV", self._map_channel(self.image_container.original, unique_vals)))
        else:
            max_channel_unique = max(len(np.unique(self.image_container.get_channel(i))) for i in range(self.image_container.channels))
            if max_channel_unique <= 100:
                for i, name in enumerate(self.image_container.channel_names):
                    channel = self.image_container.get_channel(i)
                    unique_vals = np.unique(channel)
                    results.append((f"{name} Golden Ratio HSV", self._map_channel(channel, unique_vals)))
            
            reshaped = self.image_container.original.reshape(-1, self.image_container.channels)
            unique_colors, indices = np.unique(reshaped, axis=0, return_inverse=True)
            if len(unique_colors) <= 500:
                colors = self._generate_colors(len(unique_colors))
                mapped = colors[indices].reshape(*self.image_container.original.shape[:2], 3)
                results.append(("Global Golden Ratio HSV", mapped))
        
        return results
    
    def _map_channel(self, channel, unique_vals):
        colors = self._generate_colors(len(unique_vals))
        if channel.dtype == np.uint8:
            color_map = np.zeros((256, 3), dtype=np.uint8)
            color_map[unique_vals] = colors
            return color_map[channel]
        
        output = np.zeros((*channel.shape, 3), dtype=np.uint8)
        for i, val in enumerate(unique_vals):
            output[channel == val] = colors[i]
        return output
    
    def _generate_colors(self, count):
        colors = np.zeros((count, 3), dtype=np.uint8)
        if count == 1:
            colors[0] = (128, 128, 128)
        else:
            colors[0] = (0, 0, 0)
            colors[-1] = (255, 255, 255)
            if count > 2:
                golden_ratio = (1 + 5**0.5) / 2
                hues = ((np.arange(count - 2) / golden_ratio) % 1.0) * 179
                hsv = np.stack([hues, np.full(len(hues), 204), np.full(len(hues), 229)], axis=-1).astype(np.uint8)
                colors[1:-1] = cv2.cvtColor(hsv.reshape(-1, 1, 3), cv2.COLOR_HSV2RGB).reshape(-1, 3)
        return colors
    
    def get_module_name(self):
        return "Golden Ratio HSV"
    
    @classmethod
    def get_supported_containers(cls):
        from data_containers.image_container import ImageContainer
        return [ImageContainer]