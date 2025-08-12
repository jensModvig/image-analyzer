import numpy as np
from analysis.base import AnalysisModule

class PCLBasicPropertiesModule(AnalysisModule):
    def extract_properties(self):
        properties = [
            ("Point Cloud Name", self.data_container.filepath.name, False),
            ("Full Path", self.data_container.filepath, False),
            ("Point Count", len(self.data_container.points), False),
            ("Points Data Type", str(self.data_container.points.dtype), False),
            ("Points Min Value", self.data_container.points_min, False),
            ("Points Max Value", self.data_container.points_max, False),
            ("Points Has NaN", np.isnan(self.data_container.points).any(), False),
            ("Points Has Inf", np.isinf(self.data_container.points).any(), False),
            ("Has Colors", self.data_container.has_colors, False),
        ]
        
        if self.data_container.has_colors:
            properties.extend([
                ("Colors Data Type", str(self.data_container.original_colors.dtype), False),
                ("Colors Min Value", self.data_container.colors_min, False),
                ("Colors Max Value", self.data_container.colors_max, False),
                ("Colors Has NaN", np.isnan(self.data_container.original_colors).any(), False),
                ("Colors Has Inf", np.isinf(self.data_container.original_colors).any(), False),
            ])
        
        properties.extend([
            ("Bounds", f"{self.data_container.bounds[0]} to {self.data_container.bounds[1]}", False),
            ("File Size", f"{self.data_container.filepath.stat().st_size} bytes", False)
        ])
        
        return properties
    
    def get_module_name(self):
        return "PCL Properties"
    
    @classmethod
    def get_supported_containers(cls):
        from data_containers.pcl_container import PCLContainer
        return [PCLContainer]