import numpy as np
from analysis.base import AnalysisModule

class PCLChannelStatsModule(AnalysisModule):
    def extract_properties(self):
        if not self.data_container.has_colors:
            return []
        
        properties = []
        for i, channel_name in enumerate(self.data_container.channel_names):
            channel = self.data_container.get_color_channel(i)
            min_val = np.min(channel)
            max_val = np.max(channel)
            
            properties.extend([
                (f"{channel_name} Min", int(min_val), False),
                (f"{channel_name} Max", int(max_val), False)
            ])
        
        return properties
    
    def get_module_name(self):
        return "PCL Channel Statistics"
    
    @classmethod
    def get_supported_containers(cls):
        from data_containers.pcl_container import PCLContainer
        return [PCLContainer]