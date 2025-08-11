import cv2
import numpy as np
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QLinearGradient, QBrush, QPen, QFont, QColor, QFontMetrics
from PyQt6.QtCore import Qt, QRectF, QPointF

class ColorBarWidget(QWidget):
    def __init__(self, colormap_name, min_value, max_value, width=40, height=300, 
                 dual_axis=False, unit_converter=None):
        super().__init__()
        self.colormap_name = colormap_name
        self.vmin = min_value
        self.vmax = max_value
        self.dual_axis = dual_axis
        self.unit_converter = unit_converter or (lambda x: x)
        
        range_val = max_value - min_value if max_value != min_value else 1
        step = 10 ** np.floor(np.log10(range_val / 5))
        if range_val / step > 10:
            step *= 2
        elif range_val / step > 20:
            step *= 5
            
        self.ticks = []
        tick = step * np.ceil(min_value / step)
        while tick <= max_value:
            if tick >= min_value:
                self.ticks.append(tick)
            tick += step
        if not self.ticks or self.ticks[0] > min_value:
            self.ticks.insert(0, min_value)
        if not self.ticks or self.ticks[-1] < max_value:
            self.ticks.append(max_value)
        
        metrics = QFontMetrics(QFont("", 8))
        left_width = max(metrics.horizontalAdvance(f"{v:.2f}") for v in self.ticks)
        right_width = max(metrics.horizontalAdvance(f"{self.unit_converter(v):.2f}") for v in self.ticks) if dual_axis else 0
        
        self.left_margin = left_width + 8
        self.right_margin = right_width + 8 if dual_axis else 5
        self.setFixedSize(max(width, self.left_margin + 12 + self.right_margin), height)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        
        rect = QRectF(self.left_margin, 10, 12, self.height() - 20)
        gradient = QLinearGradient(QPointF(0, rect.top()), QPointF(0, rect.bottom()))
        
        colormap = {'viridis': cv2.COLORMAP_VIRIDIS, 'plasma': cv2.COLORMAP_PLASMA, 
                   'cividis': cv2.COLORMAP_CIVIDIS, 'jet': cv2.COLORMAP_JET}.get(self.colormap_name, cv2.COLORMAP_JET)
        colors = cv2.applyColorMap(np.linspace(0, 255, 256, dtype=np.uint8).reshape(256, 1), colormap).squeeze()
        for i, color in enumerate(colors):
            gradient.setColorAt(i / 255, QColor(color[2], color[1], color[0]))
        
        painter.fillRect(rect, QBrush(gradient))
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.drawRect(rect)
        
        painter.setFont(QFont("", 8))
        metrics = QFontMetrics(QFont("", 8))
        for tick in self.ticks:
            y = int(rect.bottom() - (tick - self.vmin) / (self.vmax - self.vmin) * rect.height())
            painter.drawLine(int(rect.left() - 5), y, int(rect.left()), y)
            
            left_text = f"{tick:.2f}"
            text_width = metrics.horizontalAdvance(left_text)
            painter.drawText(int(rect.left() - 8 - text_width), y + 3, left_text)
            
            if self.dual_axis:
                painter.drawLine(int(rect.right()), y, int(rect.right() + 5), y)
                painter.drawText(int(rect.right() + 8), y + 3, f"{self.unit_converter(tick):.2f}")