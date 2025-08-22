import json
import platform
from pathlib import Path
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import Qt
from core.settings import Settings

class KeybindManager:
    def __init__(self, parent, debug=False):
        self.parent = parent
        self.debug = debug
        self.actions = {}
        self.action_configs = {}
        self.settings = Settings()
        self.defaults = self._load_defaults()
    
    def _load_defaults(self):
        config_path = Path(__file__).parent.parent / "keybinds_default.json"
        if not config_path.exists():
            raise FileNotFoundError(f"Default keybinds file not found: {config_path}")
        
        with open(config_path) as f:
            defaults = json.load(f)
        
        platform_key = {"Darwin": "macos", "Windows": "windows"}.get(platform.system(), "linux")
        result = {}
        for action, config in defaults.items():
            if platform_key not in config:
                raise KeyError(f"Platform {platform_key} not found for action {action}")
            platform_config = config[platform_key]
            self.action_configs[action] = platform_config
            result[action] = platform_config["keybind"]
        
        return result
    
    def create_action(self, action_name, text, callback):
        action = QAction(text, self.parent)
        action.triggered.connect(callback)
        user_keybind = self.settings.get("keybinds", {}).get(action_name)
        keybind_string = user_keybind or self.defaults.get(action_name, "")
        config = self.action_configs.get(action_name, {})
        
        if keybind_string and config.get("mode") == "logical":
            action.setShortcut(QKeySequence.fromString(keybind_string))
        
        self.actions[action_name] = action
        return action
    
    def handle_key_event(self, event):
        logical_seq = QKeySequence(event.modifiers().value | event.key())
        physical_code = event.nativeScanCode()
        physical_modifiers = event.modifiers().value
        
        if self.debug:
            print(f"Physical: {physical_code} (mods: {physical_modifiers}), Logical: {logical_seq.toString()}")
        
        for action_name, action in self.actions.items():
            if self.matches_action(action_name, logical_seq, physical_code, physical_modifiers):
                if self.debug:
                    print(f"  → Triggered action: {action_name}")
                action.triggered.emit()
                return True
        return False
    
    def matches_action(self, action_name, logical_seq, physical_code, physical_modifiers):
        if action_name not in self.actions:
            return False
        
        config = self.action_configs.get(action_name, {})
        mode = config.get("mode", "physical")
        user_keybind = self.settings.get("keybinds", {}).get(action_name)
        keybind = user_keybind or self.defaults.get(action_name, "")
        
        if mode == "logical":
            action = self.actions[action_name]
            return action.shortcut().matches(logical_seq) == QKeySequence.SequenceMatch.ExactMatch
        else:
            parts = keybind.split("+")
            target_scancode = int(parts[0])
            expected_mods = set(parts[1:])
            actual_mods = set()
            
            if physical_modifiers & Qt.KeyboardModifier.ShiftModifier.value:
                actual_mods.add("Shift")
            if physical_modifiers & Qt.KeyboardModifier.ControlModifier.value:
                actual_mods.add("Ctrl")
            if physical_modifiers & Qt.KeyboardModifier.AltModifier.value:
                actual_mods.add("Alt")
            if physical_modifiers & Qt.KeyboardModifier.MetaModifier.value:
                actual_mods.add("Meta")
            
            return physical_code == target_scancode and expected_mods == actual_mods
    
    def set_keybind(self, action_name, keybind_string):
        if action_name not in self.actions:
            raise KeyError(f"Action not found: {action_name}")
        
        config = self.action_configs.get(action_name, {})
        if config.get("mode") == "logical":
            self.actions[action_name].setShortcut(QKeySequence.fromString(keybind_string))
        
        user_keybinds = self.settings.get("keybinds", {})
        user_keybinds[action_name] = keybind_string
        self.settings.set("keybinds", user_keybinds)
    
    def get_keybind_text(self, action_name):
        if action_name in self.actions:
            config = self.action_configs.get(action_name, {})
            if config.get("mode") == "logical":
                return self.actions[action_name].shortcut().toString()
            else:
                return f"ScanCode: {self.defaults.get(action_name, '')}"
        return ""