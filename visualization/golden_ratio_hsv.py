import cv2
import numpy as np
from PyQt6.QtWidgets import QMenu
from PyQt6.QtCore import Qt
from visualization.base import VisualizationModule
from gui.widget_utils import create_image_widget

class GoldenRatioHSVModule(VisualizationModule):
    def __init__(self, image_container):
        super().__init__(image_container)
        self.method = "endpoints"
    
    def generate_visualizations(self):
        results = []
        
        if self.data_container.channels == 1:
            unique_vals = np.unique(self.data_container.original)
            if len(unique_vals) <= 500:
                image = self._map_channel(self.data_container.original, unique_vals)
                widget = create_image_widget(image, self.get_module_name())
                self._add_right_click_menu(widget, lambda: self._map_channel(self.data_container.original, unique_vals))
                results.append(("Golden Ratio HSV", widget))
        else:
            max_channel_unique = max(len(np.unique(self.data_container.get_channel(i))) for i in range(self.data_container.channels))
            if max_channel_unique <= 100:
                for i, name in enumerate(self.data_container.channel_names):
                    channel = self.data_container.get_channel(i)
                    unique_vals = np.unique(channel)
                    image = self._map_channel(channel, unique_vals)
                    widget = create_image_widget(image, self.get_module_name())
                    self._add_right_click_menu(widget, lambda ch=channel, uv=unique_vals: self._map_channel(ch, uv))
                    results.append((f"{name} Golden Ratio HSV", widget))
            
            reshaped = self.data_container.original.reshape(-1, self.data_container.channels)
            unique_colors, indices = np.unique(reshaped, axis=0, return_inverse=True)
            if len(unique_colors) <= 500:
                colors = self._generate_colors(len(unique_colors))
                image = colors[indices].reshape(*self.data_container.original.shape[:2], 3)
                widget = create_image_widget(image, self.get_module_name())
                self._add_right_click_menu(widget, lambda: self._generate_colors(len(unique_colors))[indices].reshape(*self.data_container.original.shape[:2], 3))
                results.append(("Global Golden Ratio HSV", widget))
        
        return results
    
    def _add_right_click_menu(self, widget, regenerate_func):
        original_mouse_press = getattr(widget, 'mousePressEvent', lambda e: None)
        
        def mouse_press_event(event):
            if event.button() == Qt.MouseButton.RightButton:
                menu = QMenu()
                about_action = menu.addAction(f"About {self.get_module_name()}")
                about_action.triggered.connect(lambda: print(f"About {self.get_module_name()}"))
                menu.addSeparator()
                
                endpoints_action = menu.addAction("Endpoints Method")
                uniform_action = menu.addAction("Uniform Method")
                
                endpoints_action.triggered.connect(lambda: self._change_method("endpoints", widget, regenerate_func))
                uniform_action.triggered.connect(lambda: self._change_method("uniform", widget, regenerate_func))
                
                menu.exec(event.globalPos())
            else:
                original_mouse_press(event)
        
        widget.mousePressEvent = mouse_press_event
    
    def _change_method(self, new_method, widget, regenerate_func):
        self.method = new_method
        new_image = regenerate_func()
        from gui.widget_utils import _create_label_from_cv2
        new_label = _create_label_from_cv2(new_image)
        widget.setPixmap(new_label.pixmap())
    
    def _map_channel(self, channel, unique_vals):
        colors = self._generate_colors(len(unique_vals))
        if channel.dtype == np.uint8:
            color_map = np.zeros((256, 3), dtype=np.uint8)
            color_map[unique_vals] = colors
            return color_map[channel]
        
        output = np.zeros((*channel.shape, 3), dtype=np.uint8)
        for i, val in enumerate(unique_vals):
            output[channel == val] = colors[i]
        return output
    
    def _generate_colors(self, count):
        if self.method == "uniform":
            return self._generate_colors_uniform(count)
        else:
            return self._generate_colors_endpoints(count)
    
    def _generate_colors_uniform(self, count):
        hues = ((np.arange(count) * 0.618034) % 1.0) * 179
        hsv = np.stack([hues, np.full(count, 204), np.full(count, 230)], axis=-1).astype(np.uint8)
        return cv2.cvtColor(hsv.reshape(-1, 1, 3), cv2.COLOR_HSV2RGB).reshape(-1, 3)
    
    def _generate_colors_endpoints(self, count):
        colors = np.zeros((count, 3), dtype=np.uint8)
        if count == 1:
            colors[0] = (128, 128, 128)
        else:
            colors[0] = (0, 0, 0)
            colors[-1] = (255, 255, 255)
            if count > 2:
                hues = ((np.arange(count - 2) * 0.618034) % 1.0) * 179
                hsv = np.stack([hues, np.full(count - 2, 204), np.full(count - 2, 230)], axis=-1).astype(np.uint8)
                colors[1:-1] = cv2.cvtColor(hsv.reshape(-1, 1, 3), cv2.COLOR_HSV2RGB).reshape(-1, 3)
        return colors
    
    def get_module_name(self):
        return "Golden Ratio HSV"
    
    @classmethod
    def get_supported_containers(cls):
        from data_containers.image_container import ImageContainer
        return [ImageContainer]