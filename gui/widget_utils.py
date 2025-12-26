from PyQt6.QtWidgets import QLabel, QApplication, QMenu
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, QObject, pyqtSignal
from gui.save_icon_overlay import add_save_functionality

class CursorSignals(QObject):
    cursor_info = pyqtSignal(str)
cursor_signals = CursorSignals()
from gui.pcl_animation import PCLAnimationController
from utils.heatmap_utils import apply_colormap_to_data, add_heatmap_right_click_menu
import cv2
import numpy as np
import json

def _create_label_from_cv2(cv2_image):
    orig_h, orig_w = cv2_image.shape[:2]
    scale = min(1.0, 400 / orig_w)
    if scale < 1.0:
        display_img = cv2.resize(cv2_image, (400, int(orig_h * scale)))
    else:
        display_img = cv2_image
    disp_h, disp_w = display_img.shape[:2]
    fmt = QImage.Format.Format_RGB888 if len(display_img.shape) == 3 else QImage.Format.Format_Grayscale8
    bpl = (3 if len(display_img.shape) == 3 else 1) * disp_w
    widget = QLabel()
    widget.setPixmap(QPixmap.fromImage(QImage(display_img.data, disp_w, disp_h, bpl, fmt)))
    widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
    widget.setMouseTracking(True)
    img_ref = cv2_image
    def mouse_move(e):
        pm = widget.pixmap()
        if pm is None:
            return
        ox = (widget.width() - pm.width()) // 2
        oy = (widget.height() - pm.height()) // 2
        px_x, px_y = e.pos().x() - ox, e.pos().y() - oy
        x, y = int(px_x / scale), int(px_y / scale)
        if 0 <= x < orig_w and 0 <= y < orig_h:
            px = img_ref[y, x]
            if len(img_ref.shape) == 3:
                cursor_signals.cursor_info.emit(f"({x}, {y})  RGB: ({px[0]}, {px[1]}, {px[2]})")
            else:
                cursor_signals.cursor_info.emit(f"({x}, {y})  Value: {px}")
    widget.mouseMoveEvent = mouse_move
    return widget

def create_image_widget(cv2_image, module_name):
    widget = add_save_functionality(_create_label_from_cv2(cv2_image))
    add_heatmap_right_click_menu(widget, module_name)
    return widget

def create_qtinteractor(cloud, container, original_data=None, colormap_change_callback=None, module_name="VTK Widget"):
    from pyvistaqt import QtInteractor

    vtk_widget = QtInteractor()
    vtk_widget.setFixedSize(400, 300)
    vtk_widget.setAcceptDrops(False)

    if 'colors' in cloud.array_names:
        vtk_widget.add_mesh(cloud, scalars='colors', rgb=True, point_size=2.0)
    else:
        vtk_widget.add_mesh(cloud, color='lightgray', point_size=2.0)

    anim = PCLAnimationController(vtk_widget, container)
    vtk_widget.animation_controller = anim

    if container:
        state = container.get_camera_state()
        vtk_widget.camera.position = state['position']
        vtk_widget.camera.focal_point = state['focal_point']
        vtk_widget.camera.up = state['up']
        vtk_widget.iren.add_observer('EndInteractionEvent', lambda o, e: container.set_camera_state({
            'position': np.array(vtk_widget.camera.position),
            'focal_point': np.array(vtk_widget.camera.focal_point),
            'up': np.array(vtk_widget.camera.up)
        }))

    def copy_transform():
        state = {'position': list(vtk_widget.camera.position),
                 'focal_point': list(vtk_widget.camera.focal_point),
                 'up': list(vtk_widget.camera.up)}
        QApplication.clipboard().setText(json.dumps(state, indent=2))

    def paste_transform():
        try:
            data = json.loads(QApplication.clipboard().text())
            vtk_widget.camera.position = data['position']
            vtk_widget.camera.focal_point = data['focal_point']
            vtk_widget.camera.up = data['up']
            vtk_widget.render()
            if container:
                container.set_camera_state({k: np.array(v) for k, v in data.items()})
        except:
            pass

    def colormap_change(name):
        if original_data is not None:
            cloud['colors'] = apply_colormap_to_data(original_data, name)
            vtk_widget.render()
        if colormap_change_callback:
            colormap_change_callback(name)

    original_mouse_press = vtk_widget.mousePressEvent
    original_key_press = vtk_widget.keyPressEvent
    original_mouse_move = vtk_widget.mouseMoveEvent

    def mouse_press_event(event):
        if event.button() == Qt.MouseButton.RightButton:
            menu = QMenu()
            menu.addAction(f"About {module_name}")
            menu.addSeparator()
            menu.addAction("Reset View", lambda: _reset_vtk_view(vtk_widget, cloud, container))
            menu.addAction("Copy Transform", copy_transform)
            menu.addAction("Paste Transform", paste_transform)
            if original_data is not None:
                menu.addSeparator()
                menu.addAction("Jet", lambda: colormap_change("jet"))
                menu.addAction("Viridis", lambda: colormap_change("viridis"))
            menu.exec(event.globalPos())
        else:
            original_mouse_press(event)

    def mouse_move_event(event):
        original_mouse_move(event)
        pos = vtk_widget.pick_mouse_position()
        if pos is not None and not any(np.isnan(pos)):
            txt = f"({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})"
            if 'colors' in cloud.array_names:
                idx = cloud.find_closest_point(pos)
                c = cloud['colors'][idx]
                txt += f"  RGB: ({c[0]}, {c[1]}, {c[2]})"
            cursor_signals.cursor_info.emit(txt)

    def key_press_event(event):
        key = event.key()
        if key == Qt.Key.Key_K:
            anim.add_keyframe()
        elif key == Qt.Key.Key_P:
            anim.toggle()
        else:
            original_key_press(event)

    vtk_widget.mousePressEvent = mouse_press_event
    vtk_widget.mouseMoveEvent = mouse_move_event
    vtk_widget.keyPressEvent = key_press_event
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
