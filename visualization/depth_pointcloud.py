import pyvista as pv
import numpy as np
import cv2
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from pyvistaqt import QtInteractor
from visualization.base import VisualizationModule
from gui.colorbar_widget import ColorBarWidget
from gui.widget_utils import get_colormap_name, get_opencv_colormap
from utils.depth_projection import project_depth_to_pointcloud

class DepthPointCloudModule(VisualizationModule):
    def generate_visualizations(self):
        results = []
        
        for i, channel_name in enumerate(self.data_container.channel_names):
            channel = self.data_container.get_channel(i)
            
            try:
                points, mask = project_depth_to_pointcloud(channel)
                if len(points) == 0:
                    continue
                
                colormap_name = get_colormap_name(channel_name)
                colormap = get_opencv_colormap(colormap_name)
                
                cloud = pv.PolyData(points)
                depth_values = channel[mask]
                
                normalized = cv2.normalize(depth_values, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                colors = cv2.applyColorMap(normalized.reshape(-1, 1), colormap)
                cloud['colors'] = cv2.cvtColor(colors, cv2.COLOR_BGR2RGB).squeeze()
                
                vtk_widget = QtInteractor()
                vtk_widget.setFixedSize(400, 300)
                vtk_widget.add_mesh(cloud, scalars='colors', rgb=True, point_size=2.0)
                
                dual_axis = channel.dtype == np.uint16
                unit_converter = (lambda x: x / 1000.0) if dual_axis else None
                
                colorbar = ColorBarWidget(
                    colormap_name, 
                    float(np.min(depth_values)), 
                    float(np.max(depth_values)),
                    width=40,
                    height=300,
                    dual_axis=dual_axis,
                    unit_converter=unit_converter
                )
                
                widget = QWidget()
                layout = QHBoxLayout(widget)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.addWidget(vtk_widget)
                layout.addWidget(colorbar)
                
                results.append((f"{channel_name} Depth PCL", widget))
                
            except (ValueError, ZeroDivisionError):
                continue
        
        return results
    
    def get_module_name(self):
        return "Depth Point Clouds"
    
    @classmethod
    def get_supported_containers(cls):
        from data_containers.image_container import ImageContainer
        return [ImageContainer]