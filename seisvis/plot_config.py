# Copyright (c) 2025 Qi Pang.
# GeoAI-INV, Xi'an Jiaotong University (XJTU).
# All rights reserved.
import matplotlib
from .opendtect_colormaps import OpendtectColormaps

class PlotConfig:
    """Configuration class for plotting, providing centralized style management"""
    
    def __init__(self):
        # Font configuration
        self.font_family = 'Times New Roman'
        self.font_weight = 'bold'
        self.tick_labelsize = 14
        self.label_fontsize = 14
        self.title_fontsize = 12
        self.legend_fontsize = 10
        self.figure_dpi = 200
        
        # Color configuration
        self.default_cmap = 'seismic'
        self.background_color = 'white'
        self.grid_alpha = 0
        
        # 3D view configuration
        self.default_elevation = 25
        self.default_azimuth = 55
        
        # Colorbar configuration
        self.colorbar_aspect = 30
        self.colorbar_shrink = 0.6
        self.colorbar_pad = 0.01
        
        # self._apply_matplotlib_settings()
    
    def apply_matplotlib_settings(self):
        """Apply global matplotlib settings"""
        matplotlib.rcParams['font.family'] = self.font_family
        matplotlib.rcParams['font.weight'] = self.font_weight
        matplotlib.rcParams['xtick.labelsize'] = self.tick_labelsize
        matplotlib.rcParams['ytick.labelsize'] = self.tick_labelsize
        matplotlib.rcParams['figure.dpi'] = self.figure_dpi
        
    def get_cmap(self, name="Petrel"):
        od_cmaps = OpendtectColormaps()
        return od_cmaps(name)
    
    def cmaps(self):
        od_cmaps = OpendtectColormaps()
        return od_cmaps.print_cmap_names()
    
    @property
    def label_style(self):
        return {
            "fontsize": self.label_fontsize,
            "fontweight": self.font_weight,
            "family": self.font_family
        }
    
    @property
    def title_style(self):
        return {
            "fontsize": self.title_fontsize,
            "fontweight": self.font_weight,
            "family": self.font_family
        }

    @property
    def legend_style(self):
        return {
            "fontsize": self.legend_fontsize,
            "family": self.font_family
        }