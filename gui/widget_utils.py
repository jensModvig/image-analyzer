from PyQt6.QtWidgets import QLabel, QWidget, QHBoxLayout
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from gui.colorbar_widget import ColorBarWidget
import cv2
import numpy as np

def create_image_widget(cv2_image):
    height, width = cv2_image.shape[:2]
    
    if len(cv2_image.shape) == 3:
        bytes_per_line = 3 * width
        q_image = QImage(cv2_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
    else:
        bytes_per_line = width
        q_image = QImage(cv2_image.data, width, height, bytes_per_line, QImage.Format.Format_Grayscale8)
    
    widget = QLabel()
    widget.setPixmap(QPixmap.fromImage(q_image))
    widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return widget

def create_heatmap_widget(cv2_image, colormap_name, min_val, max_val):
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(5)
    
    image_widget = create_image_widget(cv2_image)
    colorbar = ColorBarWidget(colormap_name, float(min_val), float(max_val), width=30, height=cv2_image.shape[0])
    
    layout.addWidget(image_widget)
    layout.addWidget(colorbar)
    return widget

def create_qtinteractor(cloud, container):
    try:
        from pyvistaqt import QtInteractor
    except ImportError:
        raise ImportError("PyVistaQt not available")
    
    vtk_widget = QtInteractor()
    vtk_widget.setFixedSize(400, 300)
    vtk_widget.setAcceptDrops(False)
    
    if 'colors' in cloud.array_names:
        vtk_widget.add_mesh(cloud, scalars='colors', rgb=True, point_size=2.0)
    else:
        vtk_widget.add_mesh(cloud, color='lightgray', point_size=2.0)
    
    state = container.get_camera_state()
    vtk_widget.camera.position = state['position']
    vtk_widget.camera.focal_point = state['focal_point']
    vtk_widget.camera.up = state['up']
    
    def update_camera():
        container.set_camera_state({
            'position': np.array(vtk_widget.camera.position),
            'focal_point': np.array(vtk_widget.camera.focal_point),
            'up': np.array(vtk_widget.camera.up)
        })
    
    vtk_widget.iren.add_observer('EndInteractionEvent', lambda obj, event: update_camera())
    return vtk_widget

def get_colormap_name(channel_name):
    mapping = {'R': 'plasma', 'G': 'viridis', 'B': 'cividis'}
    return mapping.get(channel_name, 'jet')

def get_opencv_colormap(colormap_name):
    mapping = {'plasma': cv2.COLORMAP_PLASMA, 'viridis': cv2.COLORMAP_VIRIDIS, 'cividis': cv2.COLORMAP_CIVIDIS, 'jet': cv2.COLORMAP_JET}
    return mapping.get(colormap_name, cv2.COLORMAP_JET)