from abc import ABC, abstractmethod

class FileLoader(ABC):
    @abstractmethod
    def load(self, filepath):
        pass
    
    @property
    @abstractmethod
    def extensions(self):
        pass