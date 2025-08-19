import cv2
import numpy as np
from visualization.base import VisualizationModule
from gui.widget_utils import create_image_widget

class OriginalImageModule(VisualizationModule):
    def generate_visualizations(self):
        image = self.data_container.original.copy()
        
        if image.dtype != np.uint8:
            if np.issubdtype(image.dtype, np.integer):
                dtype_info = np.iinfo(image.dtype)
                image = ((image.astype(np.float64) - dtype_info.min) * 255 / (dtype_info.max - dtype_info.min)).astype(np.uint8)
            else:
                image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        
        if self.data_container.channels == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        elif self.data_container.channels == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
        elif self.data_container.channels > 4:
            image = cv2.cvtColor(image[:, :, :3], cv2.COLOR_BGR2RGB)
        
        return [("Original", create_image_widget(image, self.get_module_name()))]
    
    def get_module_name(self):
        return "Original Image"
    
    @classmethod
    def get_supported_containers(cls):
        from data_containers.image_container import ImageContainer
        return [ImageContainer]