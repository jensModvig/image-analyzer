import cv2
import numpy as np
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QMenu
from PyQt6.QtCore import Qt
from gui.colorbar_widget import ColorBarWidget
from gui.save_icon_overlay import add_save_functionality

def get_colormap_name(channel_name):
    mapping = {'R': 'plasma', 'G': 'viridis', 'B': 'cividis'}
    return mapping.get(channel_name, 'jet')

def get_opencv_colormap(colormap_name):
    mapping = {'plasma': cv2.COLORMAP_PLASMA, 'viridis': cv2.COLORMAP_VIRIDIS, 'cividis': cv2.COLORMAP_CIVIDIS, 'jet': cv2.COLORMAP_JET}
    return mapping.get(colormap_name, cv2.COLORMAP_JET)

def apply_colormap_to_data(data, colormap_name):
    colormap = get_opencv_colormap(colormap_name)
    normalized = cv2.normalize(data, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    colors = cv2.applyColorMap(normalized, colormap)
    return cv2.cvtColor(colors, cv2.COLOR_BGR2RGB)

def add_heatmap_right_click_menu(widget, module_name, colormap_change_callback=None):
    original_mouse_press = getattr(widget, 'mousePressEvent', lambda e: None)
    
    def mouse_press_event(event):
        if event.button() == Qt.MouseButton.RightButton:
            menu = QMenu()
            
            about_action = menu.addAction(f"About {module_name}")
            about_action.triggered.connect(lambda: print(f"About {module_name}"))
            
            if colormap_change_callback:
                menu.addSeparator()
                jet_action = menu.addAction("Jet")
                viridis_action = menu.addAction("Viridis")
                jet_action.triggered.connect(lambda: colormap_change_callback("jet"))
                viridis_action.triggered.connect(lambda: colormap_change_callback("viridis"))
            
            menu.exec(event.globalPos())
        else:
            original_mouse_press(event)
    
    widget.mousePressEvent = mouse_press_event

def create_heatmap_colorbar_widget(colormap_name, min_val, max_val, height, dual_axis=False, unit_converter=None):
    return ColorBarWidget(colormap_name, float(min_val), float(max_val), 
                         width=40, height=height, dual_axis=dual_axis, unit_converter=unit_converter)

def create_heatmap_layout(image_widget, colorbar_widget):
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(5)
    layout.addWidget(image_widget)
    layout.addWidget(colorbar_widget)
    return widget