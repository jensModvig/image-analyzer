import tkinter as tk
from tkinter import ttk
import json

class AnalysisTable:
    def __init__(self, parent):
        self.parent = parent
        
        self.tree = ttk.Treeview(parent, columns=("Property", "Value", "data"), show="tree headings", displaycolumns=("Property", "Value"))
        self.tree.heading("#0", text="", anchor="w")
        self.tree.heading("Property", text="Property")
        self.tree.heading("Value", text="Value")
        
        self.tree.column("#0", width=20, minwidth=20, stretch=False)
        self.tree.column("Property", width=200, minwidth=100)
        self.tree.column("Value", width=300, minwidth=100)
        
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<Double-1>", self._on_double_click)
        self.expanded_items = set()
    

    def _serialize_for_json(self, obj):
        if isinstance(obj, dict):
            return {k: self._serialize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._serialize_for_json(item) for item in obj]
        elif hasattr(obj, 'numerator') and hasattr(obj, 'denominator'):
            return f"{obj.numerator}/{obj.denominator}"
        else:
            try:
                json.dumps(obj)
                return obj
            except (TypeError, ValueError):
                return str(obj)
    
    def update_properties(self, properties):
        self._clear_table()
        
        for prop_name, value, is_expandable in properties:
            if is_expandable:
                item_id = self.tree.insert("", "end", text="▶", 
                                         values=(prop_name, "[Expandable]"))
                serialized_value = self._serialize_for_json(value)
                self.tree.set(item_id, "data", json.dumps(serialized_value) if not isinstance(value, str) else value)
            else:
                self.tree.insert("", "end", text="", values=(prop_name, str(value)))
    
    def _on_double_click(self, event):
        item = self.tree.selection()[0]
        
        if self.tree.item(item, "text") == "▶":
            self._expand_item(item)
        elif self.tree.item(item, "text") == "▼":
            self._collapse_item(item)
    
    def _expand_item(self, item):
        self.tree.item(item, text="▼")
        
        try:
            data_str = self.tree.set(item, "data")
            if data_str.startswith('{') or data_str.startswith('['):
                data = json.loads(data_str)
            else:
                data = data_str
            
            if isinstance(data, dict):
                for key, value in data.items():
                    self.tree.insert(item, "end", text="", values=(f"  {key}", str(value)))
            elif isinstance(data, (list, tuple)):
                for i, value in enumerate(data):
                    self.tree.insert(item, "end", text="", values=(f"  [{i}]", str(value)))
            else:
                self.tree.insert(item, "end", text="", values=("  Value", str(data)))
        except:
            self.tree.insert(item, "end", text="", values=("  Error", "Could not parse data"))
        
        self.expanded_items.add(item)
    
    def _collapse_item(self, item):
        self.tree.item(item, text="▶")
        
        for child in self.tree.get_children(item):
            self.tree.delete(child)
        
        self.expanded_items.discard(item)
    
    def _clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.expanded_items.clear()