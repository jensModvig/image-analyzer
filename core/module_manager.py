from visualization.original import OriginalImageModule
from visualization.golden_ratio_hsv import GoldenRatioHSVModule
from visualization.channel_heatmap import PerChannelHeatmapModule

from analysis.basic_props import BasicPropertiesModule
from analysis.channel_stats import ChannelStatsModule
from analysis.exif_data import EXIFDataModule
from analysis.color_analysis import ColorAnalysisModule
from analysis.npz_data import NPZAnalysisModule

class ModuleManager:
    def __init__(self):
        self.visualization_modules = [
            OriginalImageModule,
            GoldenRatioHSVModule,
            PerChannelHeatmapModule
        ]
        
        self.analysis_modules = [
            BasicPropertiesModule,
            ChannelStatsModule,
            EXIFDataModule,
            ColorAnalysisModule,
            NPZAnalysisModule
        ]
    
    def get_visualizations(self, image_container):
        visualizations = []
        for module_class in self.visualization_modules:
            try:
                module = module_class(image_container)
                visualizations.extend(module.generate_visualizations())
            except Exception as e:
                print(f"Error in {module_class.__name__}: {e}")
        return visualizations
    
    def get_properties(self, image_container):
        properties = []
        for module_class in self.analysis_modules:
            try:
                module = module_class(image_container)
                properties.extend(module.extract_properties())
            except Exception as e:
                print(f"Error in {module_class.__name__}: {e}")
        return properties