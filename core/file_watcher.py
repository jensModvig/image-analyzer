import tkinter as tk
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, file_watcher, filepath):
        self.file_watcher = file_watcher
        self.filepath = str(filepath)
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path == self.filepath:
            self.file_watcher._on_file_changed()

class FileWatcher:
    def __init__(self, root, on_change_callback):
        self.root = root
        self.on_change_callback = on_change_callback
        self.observer = None
        self.debounce_timer = None
        self.watched_filepath = None
    
    def start_watching(self, filepath):
        self.stop_watching()
        
        self.watched_filepath = filepath
        self.observer = Observer()
        handler = FileChangeHandler(self, filepath)
        watch_dir = str(filepath.parent)
        self.observer.schedule(handler, watch_dir, recursive=False)
        self.observer.start()
    
    def stop_watching(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        
        if self.debounce_timer:
            self.root.after_cancel(self.debounce_timer)
            self.debounce_timer = None
    
    def _on_file_changed(self):
        if self.debounce_timer:
            self.root.after_cancel(self.debounce_timer)
        self.debounce_timer = self.root.after(200, self._debounced_callback)
    
    def _debounced_callback(self):
        self.debounce_timer = None
        if self.on_change_callback:
            self.on_change_callback()