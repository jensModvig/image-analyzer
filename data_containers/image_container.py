import cv2
import numpy as np
from data_containers.base_container import BaseContainer

class ImageContainer(BaseContainer):
    def __init__(self, filepath, data, loader_data, loader):
        super().__init__(filepath)
        self.original = data
        self.loader_data = loader_data
        self.loader = loader
        
        self.channels = self._detect_channels()
        self.channel_names = self._get_channel_names()
        self.data_min = np.min(self.original)
        self.data_max = np.max(self.original)
    
    def reload(self):
        container = self.loader.reload_container(str(self.filepath))
        self.original = container.original
        self.loader_data = container.loader_data
        self.channels = self._detect_channels()
        self.channel_names = self._get_channel_names()
        self.data_min = np.min(self.original)
        self.data_max = np.max(self.original)
        
    def _detect_channels(self):
        if len(self.original.shape) == 2:
            return 1
        return self.original.shape[2]
    
    def _get_channel_names(self):
        if self.channels == 1:
            return ["Gray"]
        elif self.channels == 3:
            return ["B", "G", "R"]
        elif self.channels == 4:
            return ["B", "G", "R", "A"]
        else:
            return [f"Ch{i}" for i in range(self.channels)]
    
    def get_channel(self, index):
        if self.channels == 1:
            return self.original
        return cv2.split(self.original)[index]