from abc import ABC, abstractmethod

class AnalysisModule(ABC):
    def __init__(self, image_container):
        self.image_container = image_container
    
    @abstractmethod
    def extract_properties(self):
        pass
    
    @abstractmethod
    def get_module_name(self):
        pass