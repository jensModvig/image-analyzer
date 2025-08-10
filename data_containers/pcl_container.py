import numpy as np
import open3d as o3d
from data_containers.base_container import BaseContainer
from file_loaders import get_loader

class PCLContainer(BaseContainer):
    def __init__(self, filepath):
        super().__init__(filepath)
        self.loader = get_loader(filepath)
        self.point_cloud, self.loader_data = self.loader.load(filepath)
        
        self.points = np.asarray(self.point_cloud.points)
        self.colors = np.asarray(self.point_cloud.colors)
        self.has_colors = len(self.colors) > 0
        self.bounds = self._calculate_bounds()
        self.current_camera_state = self._default_camera_state()
    
    def reload(self):
        self.point_cloud, self.loader_data = self.loader.reload_with_stored_params(str(self.filepath))
        self.points = np.asarray(self.point_cloud.points)
        self.colors = np.asarray(self.point_cloud.colors)
        self.has_colors = len(self.colors) > 0
        self.bounds = self._calculate_bounds()
    
    def get_basic_properties(self):
        return [
            ("Point Cloud Name", self.filepath.name, False),
            ("Full Path", self.filepath, False),
            ("Point Count", len(self.points), False),
            ("Has Colors", self.has_colors, False),
            ("Bounds", f"{self.bounds[0]} to {self.bounds[1]}", False),
            ("File Size", f"{self.filepath.stat().st_size} bytes", False)
        ]
    
    def get_camera_state(self):
        return self.current_camera_state.copy()
    
    def set_camera_state(self, state):
        self.current_camera_state = state.copy()
    
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