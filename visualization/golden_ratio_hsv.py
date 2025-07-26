import cv2
import numpy as np
from visualization.base import VisualizationModule
from utils.color_utils import generate_golden_ratio_hsv_colors

class GoldenRatioHSVModule(VisualizationModule):
    def generate_visualizations(self):
        results = []
        
        if self.image_container.channels == 1:
            unique_values = np.unique(self.image_container.original)
            hsv_image = self._create_hsv_mapping(self.image_container.original, unique_values)
            results.append(("Golden Ratio HSV", hsv_image))
        else:
            for i, channel_name in enumerate(self.image_container.channel_names):
                channel = self.image_container.get_channel(i)
                unique_values = np.unique(channel)
                hsv_image = self._create_hsv_mapping(channel, unique_values)
                results.append((f"{channel_name} Golden Ratio HSV", hsv_image))
        
        return results
    
    def _create_hsv_mapping(self, channel, unique_values):
        hsv_colors = generate_golden_ratio_hsv_colors(unique_values)
        
        output = np.zeros((*channel.shape, 3), dtype=np.uint8)
        
        for value, hsv_color in zip(unique_values, hsv_colors):
            mask = channel == value
            output[mask] = hsv_color
        
        return cv2.cvtColor(output, cv2.COLOR_HSV2RGB)
    
    def get_module_name(self):
        return "Golden Ratio HSV"