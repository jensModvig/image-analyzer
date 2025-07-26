import cv2
import numpy as np
from analysis.base import AnalysisModule

class ChannelStatsModule(AnalysisModule):
    def extract_properties(self):
        properties = []
        
        for i, channel_name in enumerate(self.image_container.channel_names):
            channel = self.image_container.get_channel(i)
            
            min_val, max_val, _, _ = cv2.minMaxLoc(channel)
            mean_val = np.mean(channel)
            
            properties.extend([
                (f"{channel_name} Min", int(min_val), False),
                (f"{channel_name} Max", int(max_val), False),
                (f"{channel_name} Mean", f"{mean_val:.2f}", False)
            ])
        
        return properties
    
    def get_module_name(self):
        return "Channel Statistics"