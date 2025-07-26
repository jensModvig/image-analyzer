#!/usr/bin/env python3

import tkinter as tk
from tkinter import filedialog, messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.app import ImageAnalyzerApp

def main():
    root = tk.Tk()
    app = ImageAnalyzerApp(root)
    
    if len(sys.argv) > 1:
        app.load_image(sys.argv[1])
    else:
        filename = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif")]
        )
        if filename:
            app.load_image(filename)
        else:
            messagebox.showinfo("Info", "Please select an image file to analyze.")
            return
    
    root.mainloop()

if __name__ == "__main__":
    main()