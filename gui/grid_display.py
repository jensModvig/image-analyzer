import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
from PIL import Image, ImageTk
import math

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
    
    def update_grid(self, visualizations):
        self._clear_grid()
        
        if not visualizations:
            return
        
        num_images = len(visualizations)
        cols = math.ceil(math.sqrt(num_images))
        rows = math.ceil(num_images / cols)
        
        max_size = 300
        
        for i, (title, image) in enumerate(visualizations):
            row = i // cols
            col = i % cols
            
            display_image = self._prepare_image_for_display(image, max_size)
            photo = ImageTk.PhotoImage(display_image)
            
            frame = ttk.Frame(self.scrollframe)
            frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            
            title_label = ttk.Label(frame, text=title, font=('Arial', 10, 'bold'))
            title_label.pack()
            
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
        for frame, _, _ in self.labels:
            frame.destroy()
        self.labels.clear()
        self.scrollframe.update_idletasks()