import numpy as np
from analysis.base import AnalysisModule

class NPZAnalysisModule(AnalysisModule):
    def extract_properties(self):
        selected_key = self.image_container.loader_data.get('selected_key')
        if not selected_key:
            return []
        
        try:
            data = np.load(self.image_container.filepath)
            all_keys = list(data.keys())
            data.close()
        except:
            return [("Selected Key", selected_key, False)]
        
        return [
            ("Selected Key", selected_key, False),
            ("All Keys", all_keys, True)
        ]
    
    def get_module_name(self):
        return "NPZ Data"