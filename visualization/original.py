import cv2
import numpy as np
from visualization.base import VisualizationModule

class OriginalImageModule(VisualizationModule):
    def generate_visualizations(self):
        image = self.image_container.original.copy()
        
        if image.dtype != np.uint8:
            image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        
        if self.image_container.channels == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        elif self.image_container.channels == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
        elif self.image_container.channels > 4:
            image = cv2.cvtColor(image[:, :, :3], cv2.COLOR_BGR2RGB)
        
        return [("Original", image)]
    
    def get_module_name(self):
        return "Original Image"