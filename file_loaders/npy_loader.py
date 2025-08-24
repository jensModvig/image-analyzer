import numpy as np
import open3d as o3d
from file_loaders.base import FileLoader
from gui.npy_column_dialog import NPYColumnDialog

class NPYLoader(FileLoader):
    def create_container(self, filepath):
        from data_containers.pcl_container import PCLContainer
        
        data = np.load(filepath)
        if len(data.shape) != 2 or data.shape[1] < 3:
            raise ValueError(f"Expected 2D array with ≥3 columns, got shape {data.shape}")
        
        selection = self.stored_params or self._show_column_dialog(data)
        if not selection:
            return None
        self.stored_params = selection
        
        points = data[:, selection['coord_start']:selection['coord_start']+3]
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        
        loader_data = {}
        
        if selection.get('color_enabled'):
            color_start = selection['color_start']
            color_channels = selection['color_channels']
            colors = data[:, color_start:color_start+color_channels]
            loader_data['original_colors'] = colors
            
            if color_channels == 1:
                display_colors = np.column_stack([colors, colors, colors])
            else:
                display_colors = colors
            pcd.colors = o3d.utility.Vector3dVector(display_colors / 255.0)
        
        return PCLContainer(filepath, pcd, loader_data, self)
    
    @property
    def extensions(self):
        return ['.npy']
    
    def _show_column_dialog(self, data):
        dialog = NPYColumnDialog(data)
        if dialog.exec() != NPYColumnDialog.DialogCode.Accepted:
            return None
        return dialog.get_selection()