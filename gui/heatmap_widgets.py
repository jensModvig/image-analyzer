from PyQt6.QtWidgets import QWidget, QHBoxLayout
from gui.widget_utils import _create_label_from_cv2, create_qtinteractor
from gui.save_icon_overlay import add_save_functionality
from utils.heatmap_utils import (apply_colormap_to_data, add_heatmap_right_click_menu, 
                                create_heatmap_colorbar_widget, create_heatmap_layout)

def create_heatmap_widget(colormap_name, min_val, max_val, original_channel_data, module_name, dual_axis=False, unit_converter=None):
    heatmap_rgb = apply_colormap_to_data(original_channel_data, colormap_name)
    image_widget = _create_label_from_cv2(heatmap_rgb)
    
    height, width = heatmap_rgb.shape[:2]
    if width > 400:
        height = int(height * 400 / width)
    
    colorbar = create_heatmap_colorbar_widget(
        colormap_name=colormap_name, min_val=min_val, max_val=max_val, 
        height=height, dual_axis=dual_axis, unit_converter=unit_converter
    )
    
    current_widgets = [image_widget, colorbar]
    widget = create_heatmap_layout(image_widget, colorbar)
    
    def regenerate_heatmap(new_colormap_name):
        new_heatmap_rgb = apply_colormap_to_data(original_channel_data, new_colormap_name)
        new_image_widget = _create_label_from_cv2(new_heatmap_rgb)
        new_colorbar = create_heatmap_colorbar_widget(
            colormap_name=new_colormap_name, min_val=min_val, max_val=max_val, 
            height=height, dual_axis=dual_axis, unit_converter=unit_converter
        )
        
        widget.layout().removeWidget(current_widgets[0])
        widget.layout().removeWidget(current_widgets[1])
        current_widgets[0].deleteLater()
        current_widgets[1].deleteLater()
        
        current_widgets[0] = new_image_widget
        current_widgets[1] = new_colorbar
        
        widget.layout().addWidget(current_widgets[0])
        widget.layout().addWidget(current_widgets[1])
    
    add_heatmap_right_click_menu(widget, module_name, regenerate_heatmap)
    return add_save_functionality(widget)

def create_vtk_heatmap_widget(cloud, container, original_data, module_name, min_val, max_val, colormap_name, dual_axis=False, unit_converter=None):
    current_colorbar = [create_heatmap_colorbar_widget(
        colormap_name=colormap_name, min_val=min_val, max_val=max_val, 
        height=300, dual_axis=dual_axis, unit_converter=unit_converter
    )]
    
    def update_colorbar(new_colormap_name):
        widget.layout().removeWidget(current_colorbar[0])
        current_colorbar[0].deleteLater()
        current_colorbar[0] = create_heatmap_colorbar_widget(
            colormap_name=new_colormap_name, min_val=min_val, max_val=max_val, 
            height=300, dual_axis=dual_axis, unit_converter=unit_converter
        )
        widget.layout().addWidget(current_colorbar[0])
    
    vtk_widget = create_qtinteractor(cloud, container, original_data, update_colorbar, module_name)
    
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(5)
    layout.addWidget(vtk_widget)
    layout.addWidget(current_colorbar[0])
    
    return widget