import numpy as np
import open3d as o3d
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLabel, QApplication, QRadioButton, QButtonGroup, QSplitter, QWidget, QSpinBox
from PyQt6.QtCore import Qt, QTimer
from file_loaders.base import FileLoader

class NPZLoader(FileLoader):
    _current_dialog = None
    
    @classmethod
    def _close_existing_dialog(cls):
        if cls._current_dialog:
            cls._current_dialog.close()
            cls._current_dialog = None
    
    def create_container(self, filepath):
        data = np.load(filepath)
        
        selection = self.stored_params
        if not selection:
            selection = self._show_selector(data)
            if not selection:
                return None
            self.stored_params = selection
        
        if selection['mode'] == 'image':
            array = data[selection['key']]
            if 'index' in selection:
                slices = tuple(selection['index'] if j == selection['axis'] else slice(None) for j in range(array.ndim))
                array = array[slices]
            from data_containers.image_container import ImageContainer
            return ImageContainer(filepath, array, selection, self)
        else:
            from data_containers.pcl_container import PCLContainer
            point_cloud, original_colors = self._project_depth(data, selection)
            enhanced_selection = selection.copy()
            if original_colors is not None:
                enhanced_selection['original_colors'] = original_colors
            return PCLContainer(filepath, point_cloud, enhanced_selection, self)
    
    @property
    def extensions(self):
        return ['.npz']
    
    def _is_indexable_image(self, array):
        if array.ndim not in [3, 4]:
            return False, -1, 0
        
        smallest_axis = np.argmin(array.shape)
        remaining_shape = [array.shape[i] for i in range(array.ndim) if i != smallest_axis]
        
        temp_array = np.zeros(remaining_shape)
        if self._is_valid_image(temp_array):
            return True, smallest_axis, array.shape[smallest_axis]
        return False, -1, 0
    
    def _show_selector(self, data):
        parent = QApplication.activeWindow()
        if parent:
            parent.raise_()
            parent.activateWindow()
        
        dialog = QDialog(parent)
        NPZLoader._current_dialog = dialog
        dialog.setWindowTitle("Select Arrays")
        dialog.setModal(True)
        dialog.resize(800, 500)
        
        if parent:
            dialog.move(parent.x() + (parent.width() - 800) // 2, parent.y() + (parent.height() - 500) // 2)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Select arrays:"))
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Image selection with indexing
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        table_widget = QTableWidget(len(data), 3)
        table_widget.setHorizontalHeaderLabels(["Key", "Shape", "Index"])
        table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        keys = list(data.keys())
        first_valid_row = -1
        
        for i, (key, array) in enumerate(data.items()):
            table_widget.setItem(i, 0, QTableWidgetItem(key))
            table_widget.setItem(i, 1, QTableWidgetItem(str(array.shape)))
            
            if self._is_valid_image(array):
                if first_valid_row == -1:
                    first_valid_row = i
            else:
                is_indexable, axis, max_index = self._is_indexable_image(array)
                if is_indexable:
                    spinbox = QSpinBox()
                    spinbox.setRange(0, max_index - 1)
                    spinbox.setValue(0)
                    table_widget.setCellWidget(i, 2, spinbox)
                    if first_valid_row == -1:
                        first_valid_row = i
                else:
                    for col in range(3):
                        item = table_widget.item(i, col)
                        if item:
                            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable & ~Qt.ItemFlag.ItemIsEnabled)
        
        if first_valid_row >= 0:
            table_widget.selectRow(first_valid_row)
        
        image_btn = QPushButton("Load as Image")
        
        left_layout.addWidget(table_widget)
        left_layout.addWidget(image_btn)
        splitter.addWidget(left_widget)
        
        # Right side: Depth projection selection
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        coord_table = QTableWidget(len(keys), 4)
        coord_table.setHorizontalHeaderLabels(["Coordinates", "Color", "Focal", "Matrix"])
        
        coord_group = QButtonGroup()
        color_group = QButtonGroup()
        focal_group = QButtonGroup()
        matrix_group = QButtonGroup()
        
        for i, (key, array) in enumerate(data.items()):
            coord_table.setVerticalHeaderItem(i, QTableWidgetItem(f"{key} {array.shape}"))
            
            if self._is_valid_coord(array):
                coord_radio = QRadioButton()
                coord_group.addButton(coord_radio, i)
                coord_table.setCellWidget(i, 0, coord_radio)
            
            if self._is_valid_color(array):
                color_radio = QRadioButton()
                color_group.addButton(color_radio, i)
                coord_table.setCellWidget(i, 1, color_radio)
            
            if self._is_valid_focal(array):
                focal_radio = QRadioButton()
                focal_group.addButton(focal_radio, i)
                coord_table.setCellWidget(i, 2, focal_radio)
            
            if self._is_valid_matrix(array):
                matrix_radio = QRadioButton()
                matrix_group.addButton(matrix_radio, i)
                coord_table.setCellWidget(i, 3, matrix_radio)
        
        project_btn = QPushButton("Project Depth Map")
        
        right_layout.addWidget(coord_table)
        right_layout.addWidget(project_btn)
        splitter.addWidget(right_widget)
        
        splitter.setSizes([300, 500])
        layout.addWidget(splitter)
        
        cancel_btn = QPushButton("Cancel")
        cancel_layout = QHBoxLayout()
        cancel_layout.addStretch()
        cancel_layout.addWidget(cancel_btn)
        layout.addLayout(cancel_layout)
        
        selection = None
        
        def project():
            nonlocal selection
            coord_id = coord_group.checkedId()
            if coord_id < 0:
                return
            
            selection = {
                'mode': 'project',
                'coord': keys[coord_id],
                'color': keys[color_group.checkedId()] if color_group.checkedId() >= 0 else None,
                'focal': keys[focal_group.checkedId()] if focal_group.checkedId() >= 0 else None,
                'matrix': keys[matrix_group.checkedId()] if matrix_group.checkedId() >= 0 else None
            }
            dialog.accept()
        
        def load_image():
            nonlocal selection
            current_row = table_widget.currentRow()
            if current_row < 0:
                return
            
            key = keys[current_row]
            array = data[key]
            
            if self._is_valid_image(array):
                selection = {'mode': 'image', 'key': key}
            else:
                is_indexable, axis, max_index = self._is_indexable_image(array)
                if is_indexable:
                    spinbox = table_widget.cellWidget(current_row, 2)
                    selection = {'mode': 'image', 'key': key, 'index': spinbox.value(), 'axis': axis}
                else:
                    return
            dialog.accept()
        
        project_btn.clicked.connect(project)
        image_btn.clicked.connect(load_image)
        cancel_btn.clicked.connect(dialog.reject)
        dialog.finished.connect(lambda: setattr(NPZLoader, '_current_dialog', None))
        
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()
        
        QTimer.singleShot(50, lambda: (dialog.raise_(), dialog.activateWindow()))
        
        return selection if dialog.exec() == QDialog.DialogCode.Accepted else None
    
    def _is_valid_image(self, array):
        return (isinstance(array, np.ndarray) and 
                np.issubdtype(array.dtype, np.number) and
                ((len(array.shape) == 2 and all(s > 1 for s in array.shape)) or
                 (len(array.shape) == 3 and array.shape[0] > 1 and array.shape[1] > 1 and array.shape[2] in {1, 3, 4})))
    
    def _is_valid_coord(self, array):
        return (isinstance(array, np.ndarray) and 
                np.issubdtype(array.dtype, np.number) and
                len(array.shape) == 2 and all(s > 1 for s in array.shape))
    
    def _is_valid_color(self, array):
        return (isinstance(array, np.ndarray) and 
                np.issubdtype(array.dtype, np.number) and
                ((len(array.shape) == 2 and all(s > 1 for s in array.shape)) or
                 (len(array.shape) == 3 and array.shape[0] > 1 and array.shape[1] > 1 and array.shape[2] in {1, 3, 4})))
    
    def _is_valid_focal(self, array):
        return (isinstance(array, np.ndarray) and 
                np.issubdtype(array.dtype, np.number) and
                (array.shape == () or (len(array.shape) == 1 and array.shape[0] == 1)))
    
    def _is_valid_matrix(self, array):
        return (isinstance(array, np.ndarray) and 
                np.issubdtype(array.dtype, np.number) and
                len(array.shape) == 2 and
                array.shape in [(3, 3), (3, 4), (4, 4)])
    
    def _project_depth(self, data, selection):
        from utils.depth_projection import project_depth_to_pointcloud
        
        depth_array = data[selection['coord']]
        focal_length = float(data[selection['focal']]) if selection['focal'] else None
        intrinsic_matrix = data[selection['matrix']] if selection['matrix'] else None
        
        points, mask = project_depth_to_pointcloud(depth_array, focal_length, intrinsic_matrix)
        
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        
        original_colors = None
        if selection['color']:
            color_array = data[selection['color']]
            if len(color_array.shape) == 2:
                original_colors = color_array[mask]
                colors = np.column_stack([original_colors, original_colors, original_colors]) / 255.0
            else:
                original_colors = color_array[mask]
                if color_array.shape[2] == 1:
                    colors = np.column_stack([original_colors[:, 0], original_colors[:, 0], original_colors[:, 0]]) / 255.0
                elif color_array.shape[2] == 3:
                    original_colors = original_colors[:, [2, 1, 0]]
                    colors = original_colors / 255.0
                elif color_array.shape[2] == 4:
                    original_colors = original_colors[:, [2, 1, 0, 3]]
                    colors = original_colors[:, :3] / 255.0
            pcd.colors = o3d.utility.Vector3dVector(colors)
        
        return pcd, original_colors