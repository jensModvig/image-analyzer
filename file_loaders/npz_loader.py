import numpy as np
import tkinter as tk
from tkinter import ttk
from file_loaders.base import FileLoader

class NPZLoader(FileLoader):
    def load(self, filepath):
        data = np.load(filepath)
        selected_key = self._show_array_selector(data)
        if selected_key is None:
            raise ValueError("No array selected")
        return data[selected_key]
    
    @property
    def extensions(self):
        return ['.npz']
    
    def _show_array_selector(self, data):
        main_window = tk._default_root
        
        root = tk.Toplevel(main_window)
        root.title("Select Array")
        root.geometry("400x300")
        
        main_x = main_window.winfo_x()
        main_y = main_window.winfo_y()
        main_width = main_window.winfo_width()
        main_height = main_window.winfo_height()
        
        popup_width = 400
        popup_height = 300
        x = main_x + (main_width - popup_width) // 2
        y = main_y + (main_height - popup_height) // 2
        
        root.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
        root.transient(main_window)
        root.grab_set()
        root.focus_set()
        
        selected_key = None
        valid_keys = []
        
        frame = ttk.Frame(root)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="Select array to load:").pack(anchor='w')
        
        listbox = tk.Listbox(frame, height=10)
        listbox.pack(fill='both', expand=True, pady=(5, 0))
        
        for key, array in data.items():
            is_valid = self._is_valid_image_array(array)
            dims_text = self._get_dimensions_text(array)
            display_text = f"{key} {dims_text}"
            
            listbox.insert('end', display_text)
            if is_valid:
                valid_keys.append(key)
            else:
                listbox.itemconfig('end', fg='gray')
        
        if valid_keys:
            first_valid_idx = list(data.keys()).index(valid_keys[0])
            listbox.selection_set(first_valid_idx)
            listbox.activate(first_valid_idx)
        
        def on_select():
            nonlocal selected_key
            selection = listbox.curselection()
            if selection:
                key = list(data.keys())[selection[0]]
                if key in valid_keys:
                    selected_key = key
                    root.destroy()
        
        def on_key(event):
            if event.keysym == 'Return':
                on_select()
            elif event.keysym == 'Escape':
                root.destroy()
        
        listbox.bind('<Double-Button-1>', lambda e: on_select())
        listbox.bind('<Return>', on_key)
        root.bind('<Key>', on_key)
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Button(button_frame, text="Select", command=on_select).pack(side='right', padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=root.destroy).pack(side='right')
        
        listbox.focus_set()
        root.wait_window()
        
        return selected_key
    
    def _is_valid_image_array(self, array):
        if not isinstance(array, np.ndarray):
            return False
        if not np.issubdtype(array.dtype, np.number):
            return False
        if len(array.shape) == 2:
            return array.shape[0] > 1 and array.shape[1] > 1
        elif len(array.shape) == 3:
            h, w, c = array.shape
            return h > 1 and w > 1 and c in {1, 3, 4}
        return False
    
    def _get_dimensions_text(self, array):
        if len(array.shape) == 2:
            return f"({array.shape[0]}×{array.shape[1]})"
        elif len(array.shape) == 3:
            return f"({array.shape[0]}×{array.shape[1]}×{array.shape[2]})"
        else:
            return f"{array.shape}"