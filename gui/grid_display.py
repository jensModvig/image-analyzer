import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
from PIL import Image, ImageTk
import math
import pyvista as pv

class GridDisplay:
    def __init__(self, parent):
        self.parent = parent
        self.canvas = tk.Canvas(parent, bg='white')
        self.scrollbar_v = ttk.Scrollbar(parent, orient='vertical', command=self.canvas.yview)
        self.scrollbar_h = ttk.Scrollbar(parent, orient='horizontal', command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=self.scrollbar_v.set, 
                            xscrollcommand=self.scrollbar_h.set)
        
        self.scrollframe = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.scrollframe, anchor='nw')
        
        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar_v.pack(side='right', fill='y')
        self.scrollbar_h.pack(side='bottom', fill='x')
        
        self.images = []
        self.labels = []
        self.plotters = []
        self.vtk_widgets = []
    
    def update_grid(self, visualizations):
        self._clear_grid()
        
        if not visualizations:
            return
        
        num_items = len(visualizations)
        cols = math.ceil(math.sqrt(num_items))
        rows = math.ceil(num_items / cols)
        
        for i, (title, content) in enumerate(visualizations):
            row = i // cols
            col = i % cols
            
            frame = ttk.Frame(self.scrollframe)
            frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            
            title_label = ttk.Label(frame, text=title, font=('Arial', 10, 'bold'))
            title_label.pack()
            
            if isinstance(content, pv.Plotter):
                try:
                    from vtk.tk.vtkTkRenderWindowInteractor import vtkTkRenderWindowInteractor
                    
                    vtk_widget = vtkTkRenderWindowInteractor(frame, rw=content.ren_win, width=300, height=300)
                    vtk_widget.Initialize()
                    vtk_widget.pack(fill='both', expand=True)
                    vtk_widget.Start()
                    
                    content.render()
                    
                    self.plotters.append(content)
                    self.vtk_widgets.append(vtk_widget)
                    self.labels.append((frame, title_label, vtk_widget))
                except ImportError:
                    error_label = ttk.Label(frame, text="VTK Tkinter support not available")
                    error_label.pack()
                    self.labels.append((frame, title_label, error_label))
            else:
                display_image = self._prepare_image_for_display(content, 300)
                photo = ImageTk.PhotoImage(display_image)
                image_label = ttk.Label(frame, image=photo)
                image_label.pack()
                self.images.append(photo)
                self.labels.append((frame, title_label, image_label))
        
        self.scrollframe.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
    
    def _prepare_image_for_display(self, cv2_image, max_size):
        height, width = cv2_image.shape[:2]
        
        if width > max_size or height > max_size:
            scale = min(max_size / width, max_size / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            cv2_image = cv2.resize(cv2_image, (new_width, new_height))
        
        if len(cv2_image.shape) == 3:
            pil_image = Image.fromarray(cv2_image)
        else:
            pil_image = Image.fromarray(cv2_image, mode='L')
        
        return pil_image
    
    def _clear_grid(self):
        self.images.clear()
        for plotter in self.plotters:
            plotter.close()
        self.plotters.clear()
        self.vtk_widgets.clear()
        for frame, _, _ in self.labels:
            frame.destroy()
        self.labels.clear()
        self.scrollframe.update_idletasks()