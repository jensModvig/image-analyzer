from PyQt6.QtWidgets import QMainWindow, QSplitter, QFileDialog, QMenu
from PyQt6.QtCore import Qt, QTimer
from file_loaders import get_loader, get_all_extensions
from file_loaders.npz_loader import NPZLoader
from core.module_manager import ModuleManager
from core.file_watcher import FileWatcher
from core.file_access import FileAccessManager
from core.ssh_manager import SSHConnectionPool
from core.remote_monitor import RemoteFileMonitor
from core.settings import Settings
from core.keybind_manager import KeybindManager
from gui.grid_display import GridDisplay
from gui.analysis_table import AnalysisTable
from gui.remote_dialog import RemoteImageDialog
from gui.widget_utils import cursor_signals

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
        self.keybind_manager = KeybindManager(self, debug=True)
        
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.setCentralWidget(self.splitter)
        
        self.grid_display = GridDisplay()
        self.analysis_table = AnalysisTable()
        
        self.splitter.addWidget(self.grid_display)
        self.splitter.addWidget(self.analysis_table)
        self.splitter.setSizes([640, 160])
        cursor_signals.cursor_info.connect(self.analysis_table.set_cursor_info)
        
        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction(self.keybind_manager.create_action("open_image", "Open Image", self._open_image))
        file_menu.addAction(self.keybind_manager.create_action("open_remote_image", "Open Remote Image", self._open_remote_image))
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        anim_menu = self.menuBar().addMenu("Animation")
        anim_menu.addAction("Add Keyframe (K)", self._anim_add_keyframe)
        anim_menu.addAction("Play/Pause (P)", self._anim_toggle)
        anim_menu.addAction("Clear Keyframes", self._anim_clear)
        anim_menu.addSeparator()
        anim_menu.addAction("Save Animation...", self._anim_save)
        anim_menu.addAction("Load Animation...", self._anim_load)

        self.setAcceptDrops(True)
    
    def keyPressEvent(self, event):
        if not self.keybind_manager.handle_key_event(event):
            super().keyPressEvent(event)
    
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
    
    def _get_active_animation(self):
        from PyQt6.QtWidgets import QWidget
        for widget in self.grid_display.findChildren(QWidget):
            if hasattr(widget, 'animation_controller'):
                print(f"Found animation controller with {len(widget.animation_controller.keyframes)} keyframes")
                return widget.animation_controller
        print("No animation controller found")
        return None

    def _anim_add_keyframe(self):
        anim = self._get_active_animation()
        if anim:
            anim.add_keyframe()

    def _anim_toggle(self):
        anim = self._get_active_animation()
        if anim:
            anim.toggle()

    def _anim_clear(self):
        anim = self._get_active_animation()
        if anim:
            anim.clear()

    def _anim_save(self):
        anim = self._get_active_animation()
        if anim:
            path, _ = QFileDialog.getSaveFileName(self, "Save Animation", "", "JSON (*.json);;Text (*.txt)")
            if path:
                anim.save(path)

    def _anim_load(self):
        anim = self._get_active_animation()
        if anim:
            path, _ = QFileDialog.getOpenFileName(self, "Load Animation", "", "JSON (*.json);;Text (*.txt)")
            if path:
                anim.load(path)

    def closeEvent(self, event):
        self.file_watcher.stop_watching()
        SSHConnectionPool.cleanup()
        RemoteFileMonitor.cleanup()
        event.accept()