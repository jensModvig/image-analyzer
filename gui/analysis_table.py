from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
import json

class AnalysisTable(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self._cursor_label = QLabel()
        self._cursor_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self._cursor_label)
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["Property", "Value"])
        self._tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self._tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self._tree)

    def set_cursor_info(self, text):
        self._cursor_label.setText(text)

    def update_properties(self, properties):
        self._tree.clear()
        for prop_name, value, is_expandable in properties:
            item = QTreeWidgetItem([prop_name, str(value) if not is_expandable else "[Expandable]"])
            if is_expandable:
                self._add_children(item, self._serialize(value))
            self._tree.addTopLevelItem(item)
    
    def _add_children(self, parent, data):
        if isinstance(data, dict):
            for key, value in data.items():
                parent.addChild(QTreeWidgetItem([f"  {key}", str(value)]))
        elif isinstance(data, (list, tuple)):
            for i, value in enumerate(data):
                parent.addChild(QTreeWidgetItem([f"  [{i}]", str(value)]))
        else:
            parent.addChild(QTreeWidgetItem(["  Value", str(data)]))
    
    def _serialize(self, obj):
        if isinstance(obj, dict):
            return {k: self._serialize(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._serialize(item) for item in obj]
        elif hasattr(obj, 'numerator') and hasattr(obj, 'denominator'):
            return f"{obj.numerator}/{obj.denominator}"
        else:
            try:
                json.dumps(obj)
                return obj
            except (TypeError, ValueError):
                return str(obj)