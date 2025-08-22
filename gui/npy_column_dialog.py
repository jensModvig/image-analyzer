from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QSpinBox, QCheckBox, QPushButton, QLabel, QRadioButton, QButtonGroup

class NPYColumnDialog(QDialog):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.setWindowTitle("NPY Column Selection")
        self.setModal(True)
        self.resize(300, 200)
        
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel(f"Shape: {data.shape}, Type: {data.dtype}"))
        
        coord_layout = QHBoxLayout()
        coord_layout.addWidget(QLabel("Coordinates:"))
        self.coord_spin = QSpinBox()
        self.coord_spin.setRange(0, max(0, data.shape[1] - 3))
        coord_layout.addWidget(self.coord_spin)
        coord_layout.addWidget(QLabel("(uses 3 columns)"))
        layout.addLayout(coord_layout)
        
        self.color_check = QCheckBox("Color:")
        layout.addWidget(self.color_check)
        
        color_layout = QHBoxLayout()
        self.color_spin = QSpinBox()
        self.color_spin.setRange(0, data.shape[1] - 1)
        self.color_spin.setEnabled(False)
        
        self.color_group = QButtonGroup()
        self.radio_1ch = QRadioButton("1ch")
        self.radio_3ch = QRadioButton("3ch")
        self.radio_3ch.setChecked(True)
        self.color_group.addButton(self.radio_1ch)
        self.color_group.addButton(self.radio_3ch)
        self.radio_1ch.setEnabled(False)
        self.radio_3ch.setEnabled(False)
        
        color_layout.addWidget(self.color_spin)
        color_layout.addWidget(self.radio_1ch)
        color_layout.addWidget(self.radio_3ch)
        layout.addLayout(color_layout)
        
        self.color_check.toggled.connect(self._toggle_color)
        
        button_layout = QHBoxLayout()
        load_btn = QPushButton("Load Point Cloud")
        load_btn.clicked.connect(self._validate_and_accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(load_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
    
    def _toggle_color(self, enabled):
        self.color_spin.setEnabled(enabled)
        self.radio_1ch.setEnabled(enabled)
        self.radio_3ch.setEnabled(enabled)
        if enabled and self.color_spin.value() + 3 > self.data.shape[1]:
            self.color_spin.setValue(max(0, self.data.shape[1] - 3))
    
    def _validate_and_accept(self):
        if self.coord_spin.value() + 3 > self.data.shape[1]:
            return
        
        if self.color_check.isChecked():
            channels = 1 if self.radio_1ch.isChecked() else 3
            if self.color_spin.value() + channels > self.data.shape[1]:
                return
        
        self.accept()
    
    def get_selection(self):
        selection = {
            'coord_start': self.coord_spin.value(),
            'color_enabled': self.color_check.isChecked()
        }
        
        if self.color_check.isChecked():
            selection.update({
                'color_start': self.color_spin.value(),
                'color_channels': 1 if self.radio_1ch.isChecked() else 3
            })
        
        return selection