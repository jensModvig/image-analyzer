import tkinter as tk
from tkinter import ttk, messagebox
from core.image_container import ImageContainer
from core.module_manager import ModuleManager
from gui.grid_display import GridDisplay
from gui.analysis_table import AnalysisTable

class ImageAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Analyzer")
        self.root.geometry("1200x800")
        
        self.image_container = None
        self.module_manager = ModuleManager()
        
        self._setup_ui()
    
    def _setup_ui(self):
        self.paned_window = ttk.PanedWindow(self.root, orient='vertical')
        self.paned_window.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.grid_frame = ttk.Frame(self.paned_window)
        self.table_frame = ttk.Frame(self.paned_window)
        
        self.paned_window.add(self.grid_frame, weight=80)
        self.paned_window.add(self.table_frame, weight=20)
        
        self.grid_display = GridDisplay(self.grid_frame)
        self.analysis_table = AnalysisTable(self.table_frame)
        
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Image", command=self._open_image)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
    
    def _open_image(self):
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif")]
        )
        if filename:
            self.load_image(filename)
    
    def load_image(self, filepath):
        self.image_container = ImageContainer(filepath)
        self._analyze_image()
    
    def _analyze_image(self):
        if not self.image_container:
            return
        
        visualizations = self.module_manager.get_visualizations(self.image_container)
        self.grid_display.update_grid(visualizations)
        
        properties = self.module_manager.get_properties(self.image_container)
        self.analysis_table.update_properties(properties)