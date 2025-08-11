from abc import ABC, abstractmethod

class FileLoader(ABC):
    def __init__(self):
        self.stored_params = None
    
    @abstractmethod
    def create_container(self, filepath):
        pass
    
    def reload_container(self, filepath):
        return self.create_container(filepath)
    
    @property
    @abstractmethod
    def extensions(self):
        pass