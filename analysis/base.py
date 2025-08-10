from abc import ABC, abstractmethod

class AnalysisModule(ABC):
    def __init__(self, data_container):
        self.data_container = data_container
    
    @abstractmethod
    def extract_properties(self):
        pass
    
    @abstractmethod
    def get_module_name(self):
        pass
    
    @classmethod
    @abstractmethod
    def get_supported_containers(cls):
        pass