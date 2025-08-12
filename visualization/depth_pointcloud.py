import pyvista as pv
import numpy as np
import cv2
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from visualization.base import VisualizationModule
from gui.colorbar_widget import ColorBarWidget
from gui.widget_utils import get_colormap_name, get_opencv_colormap, create_qtinteractor
from utils.depth_projection import project_depth_to_pointcloud

class DepthPointCloudModule(VisualizationModule):
    def generate_visualizations(self):
        results = []
        
        for i, channel_name in enumerate(self.data_container.channel_names):
            channel = self.data_container.get_channel(i)
            points, mask = project_depth_to_pointcloud(channel)
            if len(points) == 0:
                raise ValueError(f"No valid points generated for channel {channel_name}")
            
            depth_values = channel[mask]
            colormap_name = get_colormap_name(channel_name)
            
            cloud = pv.PolyData(points)
            normalized = cv2.normalize(depth_values, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            cloud['colors'] = cv2.cvtColor(cv2.applyColorMap(normalized.reshape(-1, 1), get_opencv_colormap(colormap_name)), cv2.COLOR_BGR2RGB).squeeze()
            
            is_uint16 = channel.dtype == np.uint16
            colorbar = ColorBarWidget(colormap_name, float(np.min(depth_values)), float(np.max(depth_values)),
                                    width=40, height=300, dual_axis=is_uint16, 
                                    unit_converter=(lambda x: x / 1000.0) if is_uint16 else None)
            
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(create_qtinteractor(cloud, None))
            layout.addWidget(colorbar)
            
            results.append((f"{channel_name} Depth PCL", widget))
        
        return results
    
    def get_module_name(self):
        return "Depth Point Clouds"
    
    @classmethod
    def get_supported_containers(cls):
        from data_containers.image_container import ImageContainer
        return [ImageContainer]