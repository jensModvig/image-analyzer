#!/usr/bin/env python3

import sys
import os
import signal
from PyQt6.QtWidgets import QApplication

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.app import ImageAnalyzerApp

def main():
    app = QApplication(sys.argv)
    
    def signal_handler(sig, frame):
        app.quit()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    window = ImageAnalyzerApp()
    
    if len(sys.argv) > 1:
        window.load_image(sys.argv[1])
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()