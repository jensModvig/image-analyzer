from PyQt6.QtCore import QTimer, QMetaObject, Qt, QObject, pyqtSlot
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, file_watcher, filepath):
        self.file_watcher = file_watcher
        self.filepath = str(filepath)
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path == self.filepath:
            QMetaObject.invokeMethod(self.file_watcher, "_on_file_changed", Qt.ConnectionType.QueuedConnection)

class FileWatcher(QObject):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.observer = None
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.callback)
    
    def start_watching(self, filepath):
        self.stop_watching()
        
        self.observer = Observer()
        self.observer.schedule(FileChangeHandler(self, filepath), str(filepath.parent), recursive=False)
        self.observer.start()
    
    def stop_watching(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        self.timer.stop()
    
    @pyqtSlot()
    def _on_file_changed(self):
        self.timer.stop()
        self.timer.start(200)