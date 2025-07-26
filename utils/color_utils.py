import numpy as np

def generate_golden_ratio_hsv_colors(unique_values):
    golden_ratio = (1 + 5**0.5) / 2
    colors = []
    
    for i, value in enumerate(sorted(unique_values)):
        hue = (i / golden_ratio) % 1.0
        saturation = 0.8
        brightness = 0.9
        
        hsv_color = (
            int(hue * 179),
            int(saturation * 255), 
            int(brightness * 255)
        )
        colors.append(hsv_color)
    
    return colors