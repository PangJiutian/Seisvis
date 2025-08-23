# Copyright (c) 2025 Qi Pang.
# All rights reserved.

"""
seisvis - A seismic and geophysical visualization library

Author:
    Qi Pang

Contributor:
    Hongling Chen (valuable suggestions and feedback during development)

License:
    MIT License

Purpose:
    Developed for academic research in seismic data visualization,
    including 1D well log plotting, 2D section visualization, and 3D volumetric rendering
    of geophysical properties.

Acknowledgments:
    This project leverages open-source resources and some colormaps from:
        - Matplotlib (https://matplotlib.org/)
        - OpendtectColormaps (https://github.com/whimian/OpendtectColormaps)
    
    We gratefully acknowledge the contributors of these libraries for their valuable tools
    and visual assets, which enhance the clarity and quality of seismic interpretation.
"""

# seisvis/__init__.py

from .data_cube import DataCube
from .plot_config import PlotConfig
from .plot1d import Seis1DPlotter
from .plot2d import Seis2DPlotter
from .plot3d import Seis3DPlotter


__all__ = [
    "DataCube",
    "PlotConfig",
    "Seis1DPlotter",
    "Seis2DPlotter",
    "Seis3DPlotter",
]
