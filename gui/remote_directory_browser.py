from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem, QPushButton, QLabel, QMessageBox, QLineEdit, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShortcut, QKeySequence
import stat
import re
import os
from core.ssh_manager import SSHConnectionPool

class RemoteDirectoryBrowser(QDialog):
    def __init__(self, connection_info, initial_path="/"):
        super().__init__()
        self.connection_info = connection_info
        self.current_path = initial_path
        self.selected_file_path = None
        self.sftp = None
        
        self.setWindowTitle("Browse Remote Directory")
        self.setModal(True)
        self.resize(600, 400)
        
        layout = QVBoxLayout(self)
        self.path_label = QLabel()
        layout.addWidget(self.path_label)
        
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search files and directories...")
        self.search_field.textChanged.connect(self._search)
        layout.addWidget(self.search_field)
        
        nav_layout = QHBoxLayout()
        up_button = QPushButton("Up")
        up_button.clicked.connect(lambda: self._navigate(".."))
        nav_layout.addWidget(up_button)
        nav_layout.addStretch()
        layout.addLayout(nav_layout)
        
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["Name", "Type"])
        header = self.file_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.file_tree.itemDoubleClicked.connect(self._item_double_clicked)
        layout.addWidget(self.file_tree)
        
        button_layout = QHBoxLayout()
        select_button = QPushButton("Select")
        select_button.clicked.connect(self._select_file)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(select_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(self.search_field.setFocus)
        
        ssh_client = SSHConnectionPool.get_connection(connection_info)
        self.sftp = ssh_client.open_sftp()
        self._load_directory()
    
    def closeEvent(self, event):
        if self.sftp:
            self.sftp.close()
        event.accept()
    
    def _natural_sort(self, paths):
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda path: [convert(c) for c in re.split('(\d+)', os.path.basename(str(path)))]
        return sorted(paths, key=alphanum_key)
    
    def _load_directory(self):
        try:
            self.path_label.setText(f"Path: {self.current_path}")
            self.file_tree.clear()
            self.search_field.clear()
            
            from file_loaders import get_all_extensions
            extensions = set(get_all_extensions())
            
            items = list(self.sftp.listdir_attr(self.current_path))
            directories = []
            files = []
            
            for item in items:
                if stat.S_ISDIR(item.st_mode):
                    directories.append(item)
                elif any(item.filename.lower().endswith(ext) for ext in extensions):
                    files.append(item)
            
            sorted_directories = self._natural_sort([item.filename for item in directories])
            sorted_files = self._natural_sort([item.filename for item in files])
            
            for dirname in sorted_directories:
                tree_item = QTreeWidgetItem([dirname, "Directory"])
                tree_item.setData(0, Qt.ItemDataRole.UserRole, "directory")
                self.file_tree.addTopLevelItem(tree_item)
            
            for filename in sorted_files:
                tree_item = QTreeWidgetItem([filename, "Image"])
                tree_item.setData(0, Qt.ItemDataRole.UserRole, "file")
                self.file_tree.addTopLevelItem(tree_item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load directory: {e}")
    
    def _search(self, text):
        if not text:
            return
        
        for i in range(self.file_tree.topLevelItemCount()):
            item = self.file_tree.topLevelItem(i)
            if item.text(0).lower().startswith(text.lower()):
                self.file_tree.setCurrentItem(item)
                self.file_tree.scrollToItem(item)
                break
    
    def _navigate(self, target):
        if target == ".." and self.current_path != "/":
            self.current_path = "/".join(self.current_path.rstrip("/").split("/")[:-1]) or "/"
        else:
            self.current_path = f"{self.current_path.rstrip('/')}/{target}"
        self._load_directory()
    
    def _item_double_clicked(self, item):
        item_type = item.data(0, Qt.ItemDataRole.UserRole)
        if item_type == "directory":
            self._navigate(item.text(0))
        elif item_type == "file":
            self._select_current_item()
    
    def _select_file(self):
        current_item = self.file_tree.currentItem()
        if current_item and current_item.data(0, Qt.ItemDataRole.UserRole) == "file":
            self._select_current_item()
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a file.")
    
    def _select_current_item(self):
        current_item = self.file_tree.currentItem()
        self.selected_file_path = f"{self.current_path.rstrip('/')}/{current_item.text(0)}"
        self.accept()
    
    def get_selected_file_path(self):
        return self.selected_file_path