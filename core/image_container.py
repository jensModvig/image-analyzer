import cv2
import numpy as np
from pathlib import Path
from file_loaders import get_loader

class ImageContainer:
    def __init__(self, filepath):
        self.filepath = Path(filepath)
        loader = get_loader(filepath)
        self.original = loader.load(filepath)
        
        self.channels = self._detect_channels()
        self.channel_names = self._get_channel_names()
        
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