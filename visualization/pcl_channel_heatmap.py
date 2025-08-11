import pyvista as pv
import numpy as np
import cv2
from visualization.base import VisualizationModule

class PCLChannelHeatmapModule(VisualizationModule):
    def generate_visualizations(self):
        results = []
        
        if not self.data_container.has_colors:
            return results
        
        for i, channel_name in enumerate(self.data_container.channel_names):
            channel = self.data_container.get_color_channel(i)
            colormap = self._get_colormap_for_channel(channel_name)
            
            normalized = cv2.normalize(channel, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            heatmap = cv2.applyColorMap(normalized.reshape(-1, 1), colormap)
            heatmap_rgb = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB).squeeze() / 255.0
            
            cloud = pv.PolyData(self.data_container.points)
            cloud['colors'] = (heatmap_rgb * 255).astype(np.uint8)
            
            plotter = pv.Plotter()
            plotter.add_mesh(cloud, scalars='colors', rgb=True, point_size=2.0)
            
            state = self.data_container.get_camera_state()
            plotter.camera.position = state['position']
            plotter.camera.focal_point = state['focal_point']
            plotter.camera.up = state['up']
            
            def update_camera():
                self.data_container.set_camera_state({
                    'position': np.array(plotter.camera.position),
                    'focal_point': np.array(plotter.camera.focal_point),
                    'up': np.array(plotter.camera.up)
                })
            
            plotter.iren.add_observer('EndInteractionEvent', lambda obj, event: update_camera())
            
            results.append((f"{channel_name} Heatmap", plotter))
        
        return results
    
    def _get_colormap_for_channel(self, channel_name):
        colormap_mapping = {
            'R': cv2.COLORMAP_PLASMA,
            'G': cv2.COLORMAP_VIRIDIS,
            'B': cv2.COLORMAP_CIVIDIS
        }
        return colormap_mapping.get(channel_name, cv2.COLORMAP_JET)
    
    def get_module_name(self):
        return "PCL Channel Heatmaps"
    
    @classmethod
    def get_supported_containers(cls):
        from data_containers.pcl_container import PCLContainer
        return [PCLContainer]