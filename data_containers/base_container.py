from abc import ABC, abstractmethod
from pathlib import Path

class BaseContainer(ABC):
    def __init__(self, filepath):
        self.filepath = Path(filepath)
    
    @abstractmethod
    def reload(self):
        pass
    
    @abstractmethod
    def get_basic_properties(self):
        pass