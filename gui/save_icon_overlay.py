from PyQt6.QtWidgets import QLabel, QFileDialog
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

class SaveIconOverlay(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setText("💾")
        self.setFont(QFont("", 16))
        self.setFixedSize(24, 24)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 180); color: white; border-radius: 4px;")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.hide()
        
        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            filename, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG (*.png);;JPEG (*.jpg)")
            if filename:
                if hasattr(self.parent(), 'screenshot'):
                    from PIL import Image
                    Image.fromarray(self.parent().screenshot(transparent_background=False)).save(filename)
                else:
                    if not self.parent().grab().save(filename):
                        raise RuntimeError(f"Failed to save image to {filename}")

def add_save_functionality(widget):
    icon = SaveIconOverlay(widget)
    
    original_enter = widget.enterEvent
    original_leave = widget.leaveEvent
    original_resize = widget.resizeEvent
    
    def enter_event(e):
        icon.hide_timer.stop()
        icon.move(widget.width() - 32, 8)
        icon.show()
        icon.raise_()
        original_enter(e)
    
    def leave_event(e):
        icon.hide_timer.start(100)
        original_leave(e)
    
    def resize_event(e):
        original_resize(e)
        if icon.isVisible():
            icon.move(widget.width() - 32, 8)
    
    widget.enterEvent = enter_event
    widget.leaveEvent = leave_event
    widget.resizeEvent = resize_event
    return widget