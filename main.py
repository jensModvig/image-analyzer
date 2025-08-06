#!/usr/bin/env python3

import tkinter as tk
import sys
import os
from tkinterdnd2 import TkinterDnD

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.app import ImageAnalyzerApp

def main():
    root = TkinterDnD.Tk()
    app = ImageAnalyzerApp(root)
    
    if len(sys.argv) > 1:
        app.load_image(sys.argv[1])
    
    root.mainloop()

if __name__ == "__main__":
    main()