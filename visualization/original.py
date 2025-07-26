from visualization.base import VisualizationModule

class OriginalImageModule(VisualizationModule):
    def generate_visualizations(self):
        display_image = self.image_container.get_display_image()
        return [("Original", display_image)]
    
    def get_module_name(self):
        return "Original Image"