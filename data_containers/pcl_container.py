import numpy as np
from data_containers.base_container import BaseContainer

class PCLContainer(BaseContainer):
    def __init__(self, filepath, data, loader_data, loader):
        super().__init__(filepath)
        self.point_cloud = data
        self.loader_data = loader_data
        self.loader = loader
        
        self.points = np.asarray(self.point_cloud.points)
        
        if 'original_colors' in loader_data:
            self.original_colors = loader_data['original_colors']
            self.channels = self._detect_channels()
            self.channel_names = self._get_channel_names()
        else:
            colors = np.asarray(self.point_cloud.colors)
            if len(colors) > 0:
                self.original_colors = (colors * 255).astype(np.uint8)
                self.channels = 3
                self.channel_names = ["B", "G", "R"]
            else:
                self.original_colors = np.array([])
                self.channels = 0
                self.channel_names = []
        
        self.has_colors = len(self.original_colors) > 0
        if self.has_colors:
            self.colors_min = np.min(self.original_colors)
            self.colors_max = np.max(self.original_colors)
        
        self.bounds = self._calculate_bounds()
        self.current_camera_state = self._default_camera_state()
    
    def reload(self):
        container = self.loader.reload_container(str(self.filepath))
        self.point_cloud = container.point_cloud
        self.loader_data = container.loader_data
        self.points = np.asarray(self.point_cloud.points)
        
        if 'original_colors' in container.loader_data:
            self.original_colors = container.loader_data['original_colors']
            self.channels = self._detect_channels()
            self.channel_names = self._get_channel_names()
        else:
            colors = np.asarray(self.point_cloud.colors)
            if len(colors) > 0:
                self.original_colors = (colors * 255).astype(np.uint8)
                self.channels = 3
                self.channel_names = ["B", "G", "R"]
            else:
                self.original_colors = np.array([])
                self.channels = 0
                self.channel_names = []
        
        self.has_colors = len(self.original_colors) > 0
        if self.has_colors:
            self.colors_min = np.min(self.original_colors)
            self.colors_max = np.max(self.original_colors)
            
        self.bounds = self._calculate_bounds()
    
    def get_camera_state(self):
        return self.current_camera_state.copy()
    
    def set_camera_state(self, state):
        self.current_camera_state = state.copy()
    
    def get_color_channel(self, index):
        if not self.has_colors:
            return np.array([])
        if self.channels == 1:
            return self.original_colors
        return self.original_colors[:, index]
    
    def _detect_channels(self):
        if len(self.original_colors.shape) == 1:
            return 1
        return self.original_colors.shape[1]
    
    def _get_channel_names(self):
        if self.channels == 1:
            return ["Gray"]
        elif self.channels == 3:
            return ["B", "G", "R"]
        elif self.channels == 4:
            return ["B", "G", "R", "A"]
        else:
            return [f"Ch{i}" for i in range(self.channels)]
    
    def _calculate_bounds(self):
        if len(self.points) == 0:
            return (np.array([0, 0, 0]), np.array([0, 0, 0]))
        return (np.min(self.points, axis=0), np.max(self.points, axis=0))
    
    def _default_camera_state(self):
        center = (self.bounds[0] + self.bounds[1]) / 2
        size = np.max(self.bounds[1] - self.bounds[0])
        return {
            'position': center + np.array([size, size, size]),
            'focal_point': center,
            'up': np.array([0, 0, 1])
        }