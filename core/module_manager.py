from visualization.original import OriginalImageModule
from visualization.golden_ratio_hsv import GoldenRatioHSVModule
from visualization.channel_heatmap import PerChannelHeatmapModule
from visualization.pcl_rgb import PCLRGBModule
from visualization.pcl_black import PCLBlackModule

from analysis.basic_props import BasicPropertiesModule
from analysis.channel_stats import ChannelStatsModule
from analysis.exif_data import EXIFDataModule
from analysis.color_analysis import ColorAnalysisModule
from analysis.npz_data import NPZAnalysisModule
from analysis.pcl_props import PCLBasicPropertiesModule

class ModuleManager:
    def __init__(self):
        self.visualization_modules = [
            OriginalImageModule,
            GoldenRatioHSVModule,
            PerChannelHeatmapModule,
            PCLRGBModule,
            PCLBlackModule
        ]
        
        self.analysis_modules = [
            BasicPropertiesModule,
            ChannelStatsModule,
            EXIFDataModule,
            ColorAnalysisModule,
            NPZAnalysisModule,
            PCLBasicPropertiesModule
        ]
    
    def get_visualizations(self, container):
        visualizations = []
        
        for module_class in self.visualization_modules:
            try:
                if type(container) in module_class.get_supported_containers():
                    module = module_class(container)
                    visualizations.extend(module.generate_visualizations())
            except Exception as e:
                print(f"Error in {module_class.__name__}: {e}")
        return visualizations
    
    def get_properties(self, container):
        properties = []
        
        for module_class in self.analysis_modules:
            try:
                if type(container) in module_class.get_supported_containers():
                    module = module_class(container)
                    properties.extend(module.extract_properties())
            except Exception as e:
                print(f"Error in {module_class.__name__}: {e}")
        return properties