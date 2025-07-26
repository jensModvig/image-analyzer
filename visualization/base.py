from abc import ABC, abstractmethod

class VisualizationModule(ABC):
    def __init__(self, image_container):
        self.image_container = image_container
    
    @abstractmethod
    def generate_visualizations(self):
        pass
    
    @abstractmethod
    def get_module_name(self):
        pass