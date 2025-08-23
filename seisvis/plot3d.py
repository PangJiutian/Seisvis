# Copyright (c) 2025 Qi Pang.
# All rights reserved.

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from typing import Optional, Tuple, List, Union, Dict
import warnings
import itertools

from .plot_config import PlotConfig
from .data_cube import DataCube

ClipType = Union[str, Tuple[float, float], None]
SeismicType = Dict[str, Union[str, ClipType]]
#  {'type': 'deg10','cmap': 'gray','clip': None}  # or 'rubust' or (min, max)


class Seis3DPlotter:
    """3D data plotter"""
    def __init__(self, data_cube: Union[DataCube],size=None,
                       config: Optional[PlotConfig] = None):
        """
        size: [il_start, il_end, xl_start, xl_end, t_end, t_start]
        layers: list of str, each in format 'type:name'
        """
        self.config = config or PlotConfig()
        self.config.apply_matplotlib_settings()
        
        self.cube = data_cube
        self.size = size
    
    @property
    def shape(self):
        if self.size is None:
            raise ValueError("shape requires 3D data. 'size' is not defined.")
        return [
            self.size[1] - self.size[0] + 1,
            self.size[3] - self.size[2] + 1,
            self.size[4] - self.size[5] + 1,
        ]
    
    def _validate_array(self, array: np.ndarray) -> np.ndarray:
        """Validate and preprocess input array"""
        if not isinstance(array, np.ndarray):
            array = np.array(array)

        if array.ndim != 3:
            raise ValueError(f"Input array must be 3-dimensional, got {array.ndim}D")

        if array.size == 0:
            raise ValueError("Input array cannot be empty")

        # Handle NaN values
        if np.isnan(array).any():
            warnings.warn("Array contains NaN values, replacing with array mean")
            array = np.nan_to_num(array, nan=np.nanmean(array))

        return array

    def _calculate_optimal_aspect(self, shape: Tuple[int, int, int], scale_cons=1.2):
        """Calculate optimal aspect ratio"""
        nx, ny, nz = shape
        max_index = shape.index(max(shape))
        if max_index==2:
            ar_z = 1.0
            ar_x = (nz/nx)*scale_cons
            ar_y = (nz/nx)*scale_cons
        elif max_index==0:
            ar_z = (nx/nz)
            ar_x = scale_cons
            ar_y = (nx/ny)*scale_cons
        else:
            ar_z = (ny/nz)
            ar_y = scale_cons
            ar_x = (ny/nx)*scale_cons
        return (ar_x, ar_y, ar_z)

    def _calculate_optimal_position(self, shape: Tuple[int, int, int],
                                  pos: Optional[List[int]] = None) -> List[int]:
        """Calculate optimal slice positions using golden ratio"""
        nx, ny, nz = shape

        # Use golden ratio for optimal visual positioning
        golden_ratio = 0.618
        pos = [
            int(nx * golden_ratio)+self.size[0],
            int(ny * golden_ratio)+self.size[2],
            int(nz * 0.4)+self.size[5]  # Z-axis often represents time, choose shallower position
        ]

        return pos

    def _get_clip_values(self, array: np.ndarray,
                        clip: Optional[Union[Tuple[float, float], str]] = None) -> Tuple[float, float]:
        """Calculate data clipping range with various methods"""
        if clip is None:
            return array.min(), array.max()
        elif isinstance(clip, str):
            if clip == 'robust':
                # Robust clipping using IQR
                q25, q75 = np.percentile(array, [25, 75])
                iqr = q75 - q25
                return q25 - 1.5*iqr, q75 + 1.5*iqr
            else:
                raise ValueError(f"Unsupported clip type: {clip}")
        else:
            return float(clip[0]), float(clip[1])

    def _plot_quadrants(self, ax, array: np.ndarray, fixed_coord: str,
                       pos: List[int], cmap, vmin: float, vmax: float):
        """Plot quadrant slices"""
        # pos = pos.copy()
        nx, ny, nz = array.shape
        pos[0] = pos[0]-self.size[0]
        pos[1] = pos[1]-self.size[2]
        pos[2] = pos[2]-self.size[5]
        
        # Select slice
        slice_index = {
            'x': pos[0],
            'y': pos[1],
            'z': pos[2]
        }[fixed_coord]

        index = {
            'x': (slice_index, slice(None), slice(None)),
            'y': (slice(None), slice_index, slice(None)),
            'z': (slice(None), slice(None), slice_index),
        }[fixed_coord]

        plane_data = array[index]

        # Define quadrant splits
        if fixed_coord == 'x':
            quadrants = [
                plane_data[:pos[1], :pos[2]],
                plane_data[:pos[1], pos[2]:],
                plane_data[pos[1]:, :pos[2]],
                plane_data[pos[1]:, pos[2]:]
            ]
            splits = [(0 + self.size[2], pos[1] + self.size[2], ny + self.size[2]), 
                      (0 + self.size[5], pos[2] + self.size[5], nz + self.size[5])]
        elif fixed_coord == 'y':
            quadrants = [
                plane_data[:pos[0], :pos[2]],
                plane_data[:pos[0], pos[2]:],
                plane_data[pos[0]:, :pos[2]],
                plane_data[pos[0]:, pos[2]:]
            ]
            splits = [(0 + self.size[0], pos[0] + self.size[0], nx + self.size[0]), 
                      (0 + self.size[5], pos[2] + self.size[5], nz + self.size[5])]
        elif fixed_coord == 'z':
            quadrants = [
                plane_data[:pos[0], :pos[1]],
                plane_data[:pos[0], pos[1]:],
                plane_data[pos[0]:, :pos[1]],
                plane_data[pos[0]:, pos[1]:]
            ]
            splits = [(0 + self.size[0], pos[0] + self.size[0], nx + self.size[0]), 
                      (0 + self.size[2], pos[1] + self.size[2], ny + self.size[2])]

        # Plot quadrants
        for i, quadrant in enumerate(quadrants):
            if quadrant.size == 0:
                continue

            # Enhanced color mapping
            normalized_data = (quadrant - vmin) / (vmax - vmin)
            # normalized_data = np.clip(normalized_data, 0, 1)  # Ensure valid range
            facecolors = plt.get_cmap(cmap)(normalized_data)
            facecolors[..., 3] = 0.3 # Set transparency

            # Calculate grid coordinates
            if fixed_coord == 'x':
                y_start, y_end = splits[0][(i // 2)], splits[0][(i // 2) + 1]
                z_start, z_end = splits[1][(i % 2)], splits[1][(i % 2) + 1]
                
                
                Y, Z = np.mgrid[y_start:y_end, z_start:z_end]
                X = slice_index * np.ones_like(Y) + self.size[0]
            elif fixed_coord == 'y':
                x_start, x_end = splits[0][(i // 2)], splits[0][(i // 2) + 1]
                z_start, z_end = splits[1][(i % 2)], splits[1][(i % 2) + 1]
                
                
                X, Z = np.mgrid[x_start:x_end, z_start:z_end]
                Y = slice_index * np.ones_like(X) + self.size[2]
            elif fixed_coord == 'z':
                x_start, x_end = splits[0][(i // 2)], splits[0][(i // 2) + 1]
                y_start, y_end = splits[1][(i % 2)], splits[1][(i % 2) + 1]
                
                
                X, Y = np.mgrid[x_start:x_end, y_start:y_end]
                Z = slice_index * np.ones_like(X) + self.size[5]

            ax.plot_surface(X, Y, Z, rstride=1, cstride=1,
                          facecolors=facecolors, shade=False, alpha=1)

    def plot_slices(self, show_seismic_type: Optional[SeismicType] = None,
               show_properties_type: Optional[SeismicType] = None,
               show_horizons_type: Optional[SeismicType] = None,
               show_wells_type: Optional[SeismicType] = None,
               figsize: Tuple[int, int] = (10, 8),
               pos: Optional[List[int]] = None,
               view_pos: Optional[Tuple[int, int]] = None,
               labels: Optional[Tuple[str, str, str]] = None,
               title: Optional[str] = None,
               unit_label = None,
               lighting: bool = True,
               save_path: Optional[str] = None) -> Union[Tuple[plt.Figure, plt.Axes],
                                                  Tuple[plt.Figure, plt.Axes, dict]]:
                                                         
        "Orthogonal plane visualization of 3D seismic data at any location"
        if show_seismic_type is not None:
            array = self.cube.get('seismic', show_seismic_type['type'])
            older_clip = self._get_clip_values(array, show_seismic_type['clip'])
            cmap = self.config.get_cmap(show_seismic_type['cmap'])
        
        if show_properties_type is not None:
            array = self.cube.get('properties', show_properties_type['type'])
            older_clip = self._get_clip_values(array, show_properties_type['clip'])
            cmap = self.config.get_cmap(show_properties_type['cmap'])
            
        
        # Validate input
        array = self._validate_array(array)

        # Set defaults
        if cmap is None:
            cmap = self.config.default_cmap
            
        if view_pos is None:
            view_pos = (self.config.default_elevation, self.config.default_azimuth)
            
        if labels is None:
            labels = ('Inline', 'Xline', 'Time (ms)')
            
        # Calculate positions and clipping values
        if pos is None:
            pos = self._calculate_optimal_position(array.shape, pos)

        # Create figure with enhanced styling
        fig = plt.figure(figsize=figsize, facecolor=self.config.background_color)
        ax = fig.add_subplot(111, projection='3d')

        # Set aspect ratio for better 3D perception
        aspect_ratio = self._calculate_optimal_aspect(array.shape)
        ax.set_box_aspect((array.shape[0] * aspect_ratio[0],
                          array.shape[1] * aspect_ratio[1],
                          array.shape[2] * aspect_ratio[2]))

        
        # Plot three intersecting planes
        for coord in ['x', 'y', 'z']:
            self._plot_quadrants(ax, array, coord, pos=pos.copy(), cmap=cmap, 
                                  vmin=older_clip[0], vmax=older_clip[1])
            
        if show_horizons_type is not None:
            color_iter = itertools.cycle(['lime', 'magenta', 'blue', 'cyan', 'orange', 'yellow', 'red'])
            horizons =  self.cube.get('horizons', show_horizons_type['type'])
            for name, df in horizons.items():
                X = df['X'].values.reshape(self.shape[:2])
                Y = df['Y'].values.reshape(self.shape[:2])
                Z = df['Z'].values.reshape(self.shape[:2])
                ax.plot_surface(X, Y, Z, color=next(color_iter), linewidth=0, antialiased=True)

        # overlay wells    
        if show_wells_type is not None:
            well_cmap = self.config.get_cmap(show_wells_type['cmap'])
            well_width = show_wells_type['width'] or 4
            
            all_log_df = []
            for well in self.cube.data['wells'].values():
                all_log_df.append(well.get('log'))
            combined_log = np.concatenate(all_log_df)
            older_clip = self._get_clip_values(combined_log, show_wells_type['clip'])
            
            norm_well = plt.Normalize(older_clip[0], older_clip[1])
            sm = ScalarMappable(norm=norm_well, cmap=well_cmap)
            sm.set_array(combined_log)
            
            for well_name, well in self.cube.data['wells'].items():
                well_il, well_xl = well['coord']
                # np.linspace(0, 1000, 500)
                Z = np.linspace(self.size[5], self.size[4], len(well['log']))
                ax.scatter([well_il]*len(Z), [well_xl]*len(Z), Z, 
                           c=sm.to_rgba(well['log']), s=well_width, depthshade=False)
        

        # Set viewing angle
        ax.view_init(elev=view_pos[0], azim=view_pos[1])

        # Configure axes
        ax.set_xlabel(labels[0], **self.config.label_style)
        ax.set_ylabel(labels[1], **self.config.label_style)
        ax.set_zlabel(labels[2], **self.config.label_style)

        # Set axis limits (inverted for seismic convention)
        ax.set_xlim(self.size[1], self.size[0])
        ax.set_ylim(self.size[3], self.size[2])
        ax.set_zlim(self.size[4], self.size[5])

        # Enhanced visual styling
        ax.xaxis.pane.set_visible(False)
        ax.yaxis.pane.set_visible(False)
        ax.zaxis.pane.set_visible(False)
        # ax.grid(False)
        ax.grid(True, alpha=self.config.grid_alpha)

        # Apply lighting effects
        if lighting:
            ax.xaxis.pane.fill = False
            ax.yaxis.pane.fill = False
            ax.zaxis.pane.fill = False

        # Set title with proper spacing
        if title:
            ax.set_title(title, **self.config.title_style, pad=20)

        # Add colorbar
        norm = Normalize(vmin=older_clip[0], vmax=older_clip[1])
        sm = ScalarMappable(norm=norm, cmap=cmap)
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax,
                          aspect=self.config.colorbar_aspect,
                          shrink=self.config.colorbar_shrink,
                          pad=self.config.colorbar_pad)
        if unit_label is not None:
            cbar.set_label(unit_label, **self.config.label_style, labelpad=2)
        cbar.ax.tick_params(labelsize=self.config.tick_labelsize)


        plt.tight_layout()
        plt.show()

        # Save figure if requested
        if save_path:
            plt.savefig(save_path, dpi=self.config.figure_dpi,
                       bbox_inches='tight', facecolor=fig.get_facecolor(),
                       edgecolor='none')



