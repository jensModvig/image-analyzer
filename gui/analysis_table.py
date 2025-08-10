from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView
import json

class AnalysisTable(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setHeaderLabels(["Property", "Value"])
        self.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

    def update_properties(self, properties):
        self.clear()
        
        for prop_name, value, is_expandable in properties:
            item = QTreeWidgetItem([prop_name, str(value) if not is_expandable else "[Expandable]"])
            
            if is_expandable:
                self._add_children(item, self._serialize(value))
            
            self.addTopLevelItem(item)
    
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