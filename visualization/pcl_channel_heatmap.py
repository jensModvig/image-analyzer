import pyvista as pv
import numpy as np
import cv2
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from visualization.base import VisualizationModule
from gui.colorbar_widget import ColorBarWidget
from gui.widget_utils import create_qtinteractor, get_colormap_name, get_opencv_colormap

class PCLChannelHeatmapModule(VisualizationModule):
    def generate_visualizations(self):
        results = []
        
        if not self.data_container.has_colors:
            return results
        
        for i, channel_name in enumerate(self.data_container.channel_names):
            channel = self.data_container.get_color_channel(i)
            colormap_name = get_colormap_name(channel_name)
            colormap = get_opencv_colormap(colormap_name)
            
            cloud = pv.PolyData(self.data_container.points)
            normalized = cv2.normalize(channel, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            colors = cv2.applyColorMap(normalized.reshape(-1, 1), colormap)
            cloud['colors'] = cv2.cvtColor(colors, cv2.COLOR_BGR2RGB).squeeze()
            
            vtk_widget = create_qtinteractor(cloud, self.data_container)
            colorbar = ColorBarWidget(colormap_name, float(np.min(channel)), float(np.max(channel)), width=30, height=480)
            
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(5)
            layout.addWidget(vtk_widget)
            layout.addWidget(colorbar)
            
            results.append((f"{channel_name} Heatmap", widget))
        
        return results
    
    def get_module_name(self):
        return "PCL Channel Heatmaps"
    
    @classmethod
    def get_supported_containers(cls):
        from data_containers.pcl_container import PCLContainer
        return [PCLContainer]