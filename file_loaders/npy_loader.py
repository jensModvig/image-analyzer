import numpy as np
import open3d as o3d
from file_loaders.base import FileLoader
from gui.npy_column_dialog import NPYColumnDialog

class NPYLoader(FileLoader):
    def create_container(self, filepath):
        from data_containers.pcl_container import PCLContainer
        
        data = np.load(filepath)
        if len(data.shape) != 2:
            raise ValueError(f"Expected 2D array, got shape {data.shape}")
        if data.shape[1] < 3:
            raise ValueError(f"Array must have at least 3 columns for coordinates, got {data.shape[1]}")
        
        selection = self.stored_params
        if not selection:
            selection = self._show_column_dialog(data)
            if not selection:
                return None
            self.stored_params = selection
        
        points = data[:, selection['coord_start']:selection['coord_start']+3]
        
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        
        loader_data = selection.copy()
        if selection.get('color_enabled'):
            color_start = selection['color_start']
            color_channels = selection['color_channels']
            colors = data[:, color_start:color_start+color_channels]
            
            if color_channels == 1:
                colors = np.column_stack([colors, colors, colors])
            
            loader_data['original_colors'] = colors.astype(np.uint8)
            pcd.colors = o3d.utility.Vector3dVector(colors / 255.0)
        
        return PCLContainer(filepath, pcd, loader_data, self)
    
    @property
    def extensions(self):
        return ['.npy']
    
    def _show_column_dialog(self, data):
        dialog = NPYColumnDialog(data)
        return dialog.get_selection() if dialog.exec() == NPYColumnDialog.DialogCode.Accepted else None