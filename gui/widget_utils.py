from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from gui.save_icon_overlay import add_save_functionality
from utils.heatmap_utils import apply_colormap_to_data, add_heatmap_right_click_menu
import cv2
import numpy as np

def _create_label_from_cv2(cv2_image):
    height, width = cv2_image.shape[:2]
    if width > 400:
        scale = 400 / width
        cv2_image = cv2.resize(cv2_image, (400, int(height * scale)))
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

def create_image_widget(cv2_image, module_name):
    widget = add_save_functionality(_create_label_from_cv2(cv2_image))
    add_heatmap_right_click_menu(widget, module_name)
    return widget

def create_qtinteractor(cloud, container, original_data=None, colormap_change_callback=None, module_name="VTK Widget"):
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
    
    if container:
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
    
    def colormap_change_wrapper(new_colormap_name):
        if original_data is not None:
            new_colors = apply_colormap_to_data(original_data, new_colormap_name)
            cloud['colors'] = new_colors
            vtk_widget.render()
        if colormap_change_callback:
            colormap_change_callback(new_colormap_name)
    
    def reset_view():
        _reset_vtk_view(vtk_widget, cloud, container)
    
    original_mouse_press = getattr(vtk_widget, 'mousePressEvent', lambda e: None)
    
    def mouse_press_event(event):
        if event.button() == Qt.MouseButton.RightButton:
            from PyQt6.QtWidgets import QMenu
            menu = QMenu()
            
            about_action = menu.addAction(f"About {module_name}")
            about_action.triggered.connect(lambda: print(f"About {module_name}"))
            menu.addSeparator()
            
            reset_action = menu.addAction("Reset View")
            reset_action.triggered.connect(reset_view)
            
            if original_data is not None:
                menu.addSeparator()
                jet_action = menu.addAction("Jet")
                viridis_action = menu.addAction("Viridis")
                jet_action.triggered.connect(lambda: colormap_change_wrapper("jet"))
                viridis_action.triggered.connect(lambda: colormap_change_wrapper("viridis"))
            
            menu.exec(event.globalPos())
        else:
            original_mouse_press(event)
    
    vtk_widget.mousePressEvent = mouse_press_event
    
    return add_save_functionality(vtk_widget)

def _reset_vtk_view(vtk_widget, cloud, container):
    if container and hasattr(container, 'get_camera_state'):
        state = container.get_camera_state()
        vtk_widget.camera.position = state['position']
        vtk_widget.camera.focal_point = state['focal_point']
        vtk_widget.camera.up = state['up']
    else:
        center = cloud.center
        size = cloud.length
        vtk_widget.camera.position = center + np.array([size, size, size])
        vtk_widget.camera.focal_point = center
        vtk_widget.camera.up = np.array([0, 0, 1])
    vtk_widget.render()