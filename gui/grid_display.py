from PyQt6.QtWidgets import QScrollArea, QGridLayout, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont, QImage
import cv2
import numpy as np
import math
import pyvista as pv

class GridDisplay(QScrollArea):
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        
        self.scroll_widget = QWidget()
        self.grid_layout = QGridLayout(self.scroll_widget)
        self.setWidget(self.scroll_widget)
        
        self.plotters = []
        self.vtk_widgets = []
    
    def update_grid(self, visualizations):
        self._clear_grid()
        
        if not visualizations:
            return
        
        cols = math.ceil(math.sqrt(len(visualizations)))
        
        for i, (title, content) in enumerate(visualizations):
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setContentsMargins(5, 5, 5, 5)
            
            title_label = QLabel(title)
            title_label.setFont(QFont("", 0, QFont.Weight.Bold))
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title_label)
            
            if isinstance(content, pv.Plotter):
                try:
                    from pyvistaqt import QtInteractor
                    
                    vtk_widget = QtInteractor(container)
                    vtk_widget.setFixedSize(300, 300)
                    
                    for actor in content.renderer.actors.values():
                        vtk_widget.add_actor(actor)
                    
                    vtk_widget.camera = content.camera
                    vtk_widget.reset_camera()
                    
                    layout.addWidget(vtk_widget)
                    
                    self.plotters.append(content)
                    self.vtk_widgets.append(vtk_widget)
                    
                except ImportError:
                    error_label = QLabel("PyVistaQt not available")
                    error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    layout.addWidget(error_label)
            else:
                pixmap = self._cv2_to_pixmap(content, 300)
                image_label = QLabel()
                image_label.setPixmap(pixmap)
                image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(image_label)
            
            self.grid_layout.addWidget(container, i // cols, i % cols)
    
    def _cv2_to_pixmap(self, cv2_image, max_size):
        height, width = cv2_image.shape[:2]
        
        if width > max_size or height > max_size:
            scale = min(max_size / width, max_size / height)
            cv2_image = cv2.resize(cv2_image, (int(width * scale), int(height * scale)))
            height, width = cv2_image.shape[:2]
        
        if len(cv2_image.shape) == 3:
            bytes_per_line = 3 * width
            q_image = QImage(cv2_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        else:
            bytes_per_line = width
            q_image = QImage(cv2_image.data, width, height, bytes_per_line, QImage.Format.Format_Grayscale8)
        
        return QPixmap.fromImage(q_image)
    
    def _clear_grid(self):
        for plotter in self.plotters:
            plotter.close()
        self.plotters.clear()
        self.vtk_widgets.clear()
        
        while self.grid_layout.count():
            self.grid_layout.takeAt(0).widget().deleteLater()