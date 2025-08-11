from PyQt6.QtWidgets import QScrollArea, QGridLayout, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import math

class GridDisplay(QScrollArea):
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        
        self.scroll_widget = QWidget()
        self.grid_layout = QGridLayout(self.scroll_widget)
        self.setWidget(self.scroll_widget)
    
    def update_grid(self, visualizations):
        self._clear_grid()
        
        if not visualizations:
            return
        
        cols = math.ceil(math.sqrt(len(visualizations)))
        
        for i, (title, widget) in enumerate(visualizations):
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setContentsMargins(5, 5, 5, 5)
            
            title_label = QLabel(title)
            title_label.setFont(QFont("", 0, QFont.Weight.Bold))
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title_label)
            
            layout.addWidget(widget)
            
            self.grid_layout.addWidget(container, i // cols, i % cols)
    
    def _clear_grid(self):
        while self.grid_layout.count():
            self.grid_layout.takeAt(0).widget().deleteLater()