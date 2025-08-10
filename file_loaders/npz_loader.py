import numpy as np
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QLabel, QApplication
from PyQt6.QtCore import Qt, QTimer
from file_loaders.base import FileLoader

class ValidOnlyListWidget(QListWidget):
    def __init__(self, valid_indices):
        super().__init__()
        self.valid_indices = valid_indices
    
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            current = self.currentRow()
            direction = 1 if event.key() == Qt.Key.Key_Down else -1
            
            next_valid = None
            for i in range(current + direction, len(self.valid_indices) if direction > 0 else -1, direction):
                if i in self.valid_indices:
                    next_valid = i
                    break
            
            if next_valid is not None:
                self.setCurrentRow(next_valid)
        else:
            super().keyPressEvent(event)

class NPZLoader(FileLoader):
    def __init__(self):
        self.selected_key = None
    
    def load(self, filepath):
        data = np.load(filepath)
        self.selected_key = self._show_selector(data)
        if not self.selected_key:
            raise ValueError("No array selected")
        return data[self.selected_key], {'selected_key': self.selected_key}
    
    def reload_with_stored_params(self, filepath):
        if not self.selected_key:
            return self.load(filepath)
        
        data = np.load(filepath)
        if self.selected_key not in data:
            valid_keys = [k for k in data.keys() if self._is_valid(data[k])]
            if not valid_keys:
                raise ValueError(f"No valid arrays in {filepath}")
            self.selected_key = valid_keys[0]
        
        return data[self.selected_key], {'selected_key': self.selected_key}
    
    @property
    def extensions(self):
        return ['.npz']
    
    @property
    def container_type(self):
        from data_containers.image_container import ImageContainer
        return ImageContainer
    
    def _show_selector(self, data):
        parent = QApplication.activeWindow()
        
        if parent:
            parent.raise_()
            parent.activateWindow()
        
        dialog = QDialog(parent)
        dialog.setWindowTitle("Select Array")
        dialog.setModal(True)
        dialog.resize(400, 300)
        
        if parent:
            dialog.move(parent.x() + (parent.width() - 400) // 2, parent.y() + (parent.height() - 300) // 2)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Select array to load:"))
        
        valid_indices = []
        keys = list(data.keys())
        
        for i, (key, array) in enumerate(data.items()):
            if self._is_valid(array):
                valid_indices.append(i)
        
        list_widget = ValidOnlyListWidget(valid_indices)
        
        for i, (key, array) in enumerate(data.items()):
            dims = f"({array.shape[0]}×{array.shape[1]})" if len(array.shape) == 2 else f"{array.shape}"
            item_text = f"{key} {dims}"
            list_widget.addItem(item_text)
            
            if i not in valid_indices:
                item = list_widget.item(i)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable & ~Qt.ItemFlag.ItemIsEnabled)
        
        if valid_indices:
            list_widget.setCurrentRow(valid_indices[0])
        
        layout.addWidget(list_widget)
        
        buttons = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        select_btn = QPushButton("Select")
        select_btn.setDefault(True)
        
        buttons.addStretch()
        buttons.addWidget(cancel_btn)
        buttons.addWidget(select_btn)
        layout.addLayout(buttons)
        
        selected_key = None
        
        def select():
            nonlocal selected_key
            current_row = list_widget.currentRow()
            if current_row >= 0 and current_row in valid_indices:
                selected_key = keys[current_row]
                dialog.accept()
        
        select_btn.clicked.connect(select)
        cancel_btn.clicked.connect(dialog.reject)
        list_widget.itemDoubleClicked.connect(select)
        
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()
        
        QTimer.singleShot(50, lambda: (
            dialog.raise_(),
            dialog.activateWindow(),
            list_widget.setFocus()
        ))
        
        return selected_key if dialog.exec() == QDialog.DialogCode.Accepted else None
    
    def _is_valid(self, array):
        return (isinstance(array, np.ndarray) and 
                np.issubdtype(array.dtype, np.number) and
                ((len(array.shape) == 2 and all(s > 1 for s in array.shape)) or
                 (len(array.shape) == 3 and array.shape[0] > 1 and array.shape[1] > 1 and array.shape[2] in {1, 3, 4})))