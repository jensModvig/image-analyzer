import cv2
import numpy as np
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt

class ColorBarWidget(QLabel):
    def __init__(self, colormap_name, min_value, max_value, width=30, height=200):
        super().__init__()
        self.setFixedSize(width, height)
        
        colormap = self._get_opencv_colormap(colormap_name)
        gradient = np.linspace(255, 0, height, dtype=np.uint8).reshape(height, 1)
        colorbar = cv2.applyColorMap(gradient, colormap)
        colorbar = cv2.cvtColor(colorbar, cv2.COLOR_BGR2RGB)
        colorbar = np.repeat(colorbar, width, axis=1)
        
        ticks = [(max_value, 10), (min_value, height-5)]
        if height > 80:
            mid = (min_value + max_value) / 2
            ticks.insert(1, (mid, height//2))
        
        for value, y_pos in ticks:
            text = f'{value:.3g}' if isinstance(value, float) else str(int(value))
            cv2.putText(colorbar, text, (2, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.25, (255, 255, 255), 1)
        
        q_image = QImage(colorbar.data, width, height, width * 3, QImage.Format.Format_RGB888)
        self.setPixmap(QPixmap.fromImage(q_image))
    
    def _get_opencv_colormap(self, name):
        mapping = {
            'plasma': cv2.COLORMAP_PLASMA,
            'viridis': cv2.COLORMAP_VIRIDIS,
            'cividis': cv2.COLORMAP_CIVIDIS,
            'jet': cv2.COLORMAP_JET
        }
        return mapping.get(name, cv2.COLORMAP_JET)