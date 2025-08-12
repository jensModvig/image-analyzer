from PyQt6.QtWidgets import QMainWindow, QSplitter, QFileDialog
from PyQt6.QtCore import Qt, QTimer
from file_loaders import get_loader, get_all_extensions
from file_loaders.npz_loader import NPZLoader
from core.module_manager import ModuleManager
from core.file_watcher import FileWatcher
from core.file_access import FileAccessManager
from core.ssh_manager import SSHConnectionPool
from core.remote_monitor import RemoteFileMonitor
from core.settings import Settings
from gui.grid_display import GridDisplay
from gui.analysis_table import AnalysisTable
from gui.remote_dialog import RemoteImageDialog

class ImageAnalyzerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Analyzer")
        self.resize(1200, 800)
        
        screen = self.screen().availableGeometry()
        self.move((screen.width() - 1200) // 2, (screen.height() - 800) // 2)
        
        self.data_container = None
        self.module_manager = ModuleManager()
        self.file_watcher = FileWatcher(self._reload_current_file)
        self.settings = Settings()
        
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.setCentralWidget(self.splitter)
        
        self.grid_display = GridDisplay()
        self.analysis_table = AnalysisTable()
        
        self.splitter.addWidget(self.grid_display)
        self.splitter.addWidget(self.analysis_table)
        self.splitter.setSizes([640, 160])
        
        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction("Open Image", self._open_image)
        file_menu.addAction("Open Remote Image", self._open_remote_image)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)
        
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        if files:
            NPZLoader._close_existing_dialog()
            QTimer.singleShot(100, lambda: self.load_image(files[0]))
    
    def _open_image(self):
        NPZLoader._close_existing_dialog()
        extensions = get_all_extensions()
        ext_pattern = " ".join(f"*{ext}" for ext in extensions)
        filename, _ = QFileDialog.getOpenFileName(self, "Select Image", "", f"All supported files ({ext_pattern})")
        if filename:
            self.load_image(filename)
    
    def _open_remote_image(self):
        dialog = RemoteImageDialog()
        if dialog.exec() == RemoteImageDialog.DialogCode.Accepted:
            connection_info = dialog.get_connection_info()
            remote_path = dialog.get_remote_path()
            if not remote_path:
                return
            
            config_host = connection_info.get('config_host')
            if config_host:
                remote_identifier = f"{config_host}:{remote_path}"
            else:
                remote_identifier = f"{connection_info['hostname']}:{remote_path}"
            
            self.load_image((remote_identifier, connection_info))
    
    def load_image(self, filepath):
        resolved_path = FileAccessManager.resolve_path(filepath)
        
        loader = get_loader(resolved_path)
        container = loader.create_container(resolved_path)
        if container is None:
            return
        
        self.file_watcher.stop_watching()
        self.data_container = container
        self._analyze_image()
        self.file_watcher.start_watching(self.data_container.filepath)
        
        self.raise_()
        self.activateWindow()
        self.setFocus()
    
    def _analyze_image(self):
        if not self.data_container:
            return
        
        self.grid_display.update_grid(self.module_manager.get_visualizations(self.data_container))
        self.analysis_table.update_properties(self.module_manager.get_properties(self.data_container))
    
    def _reload_current_file(self):
        if self.data_container:
            self.data_container.reload()
            self._analyze_image()
    
    def closeEvent(self, event):
        self.file_watcher.stop_watching()
        SSHConnectionPool.cleanup()
        RemoteFileMonitor.cleanup()
        event.accept()