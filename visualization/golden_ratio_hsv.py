import cv2
import numpy as np
import random
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
                colors = self._generate_colors(len(unique_colors), indices.reshape(self.data_container.original.shape[:2]))
                image = colors[indices].reshape(*self.data_container.original.shape[:2], 3)
                widget = create_image_widget(image, self.get_module_name())
                self._add_right_click_menu(widget, lambda: self._generate_colors(len(unique_colors), indices.reshape(self.data_container.original.shape[:2]))[indices].reshape(*self.data_container.original.shape[:2], 3))
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
        colors = self._generate_colors(len(unique_vals), channel)
        if channel.dtype == np.uint8:
            color_map = np.zeros((256, 3), dtype=np.uint8)
            color_map[unique_vals] = colors
            return color_map[channel]
        
        output = np.zeros((*channel.shape, 3), dtype=np.uint8)
        for i, val in enumerate(unique_vals):
            output[channel == val] = colors[i]
        return output
    
    def _generate_colors(self, count, labeled_image):
        if self.method == "uniform":
            return self._generate_colors_uniform(count, labeled_image)
        else:
            return self._generate_colors_endpoints(count, labeled_image)
    
    def _compute_normed_spatial_distances(self, labeled_image, labels):
        n = len(labels)
        distances = np.zeros((n, n))
        max_spatial_dist = np.linalg.norm(labeled_image.shape[:2])
        
        for i in range(n):
            mask_i = (labeled_image == labels[i]).astype(np.uint8)
            dist_transform = cv2.distanceTransform(1 - mask_i, cv2.DIST_L2, 3)
            
            for j in range(i + 1, n):
                mask_j = labeled_image == labels[j]
                distances[i, j] = distances[j, i] = np.min(dist_transform[mask_j])
        
        return distances / max_spatial_dist
    
    def _compute_normed_color_distances(self, colors):
        colors_hsv = cv2.cvtColor(colors.reshape(1, -1, 3), cv2.COLOR_RGB2HSV)[0]
        hues = colors_hsv[:, 0].astype(float)
        hue_diff = hues[:, None] - hues[None, :]
        hue_color_distance = np.minimum(np.abs(hue_diff), 180 - np.abs(hue_diff))
        return hue_color_distance / 90
    
    def _optimize_assignment(self, base_colors, labeled_image, labels, n_iterations=1000):
        spatial_dist = self._compute_normed_spatial_distances(labeled_image, labels)
        color_dist = self._compute_normed_color_distances(base_colors)
        
        best_loss = float('inf')
        best_assignment = list(range(len(labels)))
        
        for _ in range(n_iterations):
            c = len(labels)
            assignment = list(range(c))
            random.shuffle(assignment)

            loss = sum((1 - spatial_dist[i,j])**100 * (1 - color_dist[assignment[i], assignment[j]])**2 
                    for i in range(len(labels)) for j in range(i+1, len(labels)))
            
            if loss < best_loss:
                best_loss = loss
                best_assignment = assignment
        
        print(best_loss)
        
        return base_colors[best_assignment]
    
    def _generate_uniform_colors(self, count):
        """Generate count uniform colors using golden ratio spacing"""
        hues = np.linspace(0, 180, count+1)[:-1]
        hsv = np.stack([hues, np.full(count, 204), np.full(count, 230)], axis=-1).astype(np.uint8)
        return cv2.cvtColor(hsv.reshape(-1, 1, 3), cv2.COLOR_HSV2RGB).reshape(-1, 3)

    def _generate_colors_uniform(self, count, labeled_image):
        colors = self._generate_uniform_colors(count)
        labels = np.unique(labeled_image)
        return self._optimize_assignment(colors, labeled_image, labels)

    def _generate_colors_endpoints(self, count, labeled_image):
        if count == 1:
            return np.array([[128, 128, 128]], dtype=np.uint8)
        
        labels = np.unique(labeled_image)
        labels = labels[labels >= 0][:count]
        
        colors = np.zeros((count, 3), dtype=np.uint8)
        colors[0] = (0, 0, 0) 
        colors[-1] = (255, 255, 255)
        
        if count > 2:
            middle_colors = self._generate_uniform_colors(count - 2)
            middle_labels = labels[1:-1]
            optimized_middle = self._optimize_assignment(middle_colors, labeled_image, middle_labels)
            colors[1:-1] = optimized_middle
        
        return colors
    
    def get_module_name(self):
        return "Golden Ratio HSV"
    
    @classmethod
    def get_supported_containers(cls):
        from data_containers.image_container import ImageContainer
        return [ImageContainer]