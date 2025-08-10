import cv2
import numpy as np
from data_containers.base_container import BaseContainer
from file_loaders import get_loader

class ImageContainer(BaseContainer):
    def __init__(self, filepath):
        super().__init__(filepath)
        self.loader = get_loader(filepath)
        self.original, self.loader_data = self.loader.load(filepath)
        
        self.channels = self._detect_channels()
        self.channel_names = self._get_channel_names()
        self.data_min = np.min(self.original)
        self.data_max = np.max(self.original)
    
    def reload(self):
        self.original, self.loader_data = self.loader.reload_with_stored_params(str(self.filepath))
        self.channels = self._detect_channels()
        self.channel_names = self._get_channel_names()
        self.data_min = np.min(self.original)
        self.data_max = np.max(self.original)
    
    def get_basic_properties(self):
        return [
            ("Image Name", self.filepath.name, False),
            ("Full Path", self.filepath, False),
            ("Width", self.original.shape[1], False),
            ("Height", self.original.shape[0], False),
            ("Channels", self.channels, False),
            ("Data Type", str(self.original.dtype), False),
            ("File Size", f"{self.filepath.stat().st_size} bytes", False)
        ]
        
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