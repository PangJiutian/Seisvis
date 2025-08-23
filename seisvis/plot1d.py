# Copyright (c) 2025 Qi Pang.
# All rights reserved.
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional, Tuple, List
import itertools
from .plot_config import PlotConfig

class Seis1DPlotter:
    """1D data plotter"""
    
    def __init__(self, config: Optional[PlotConfig] = None):
        self.config = config or PlotConfig()
        self.config.apply_matplotlib_settings()

    def plot_groups(self,
                    data_groups: List[List[np.ndarray]],
                    t_start=None,
                    dt = 1,
                    titles: Optional[List[str]] = None,
                    legends: Optional[List[str]] = None,
                    line_styles: Optional[List[str]] = None,
                    vis_type='v',
                    figsize: Tuple[int, int] = (4, 11),
                    save_path: Optional[str] = None):
        """
        Plot each data group (e.g., each variable) in a subplot, all in one figure.
        """
        if isinstance(data_groups, np.ndarray):
            data_groups = [[data_groups]]
        elif isinstance(data_groups, list) and isinstance(data_groups[0], np.ndarray):
            data_groups = [data_groups]
            
        if isinstance(titles, str):
            titles = [titles]
            
        if isinstance(legends, str):
            legends = [legends]    
            
        n_groups = len(data_groups)
        n_traces = len(data_groups[0])
        
        # --- Check all groups have the same number of traces ---
        for g in data_groups:
            if len(g) != n_traces:
                raise ValueError("All groups must have the same number of traces (methods).")
        
        # --- Check titles ---
        if titles is not None:
            if len(titles) != n_groups:
                raise ValueError(f"Number of titles {len(titles)} must match number of groups {n_groups}.")
                
        # --- Check legends ---
        if legends is not None:
            if len(legends) != n_traces:
                raise ValueError(f"Number of legends {len(legends)} must match number of traces per group {n_traces}.")
        
        if t_start is None:
            time = (np.arange(data_groups[0][0].shape[0])) * dt
        else:
            time = (np.arange(data_groups[0][0].shape[0])) * dt + t_start
    
        if line_styles is None:
            line_styles = ['-'] * n_traces
    
        color_iter = itertools.cycle([
            'black', 'blue', 'red', 'green', 'orange',
            'purple', 'cyan', 'magenta', 'brown', 'olive'
        ])
        color_list = list(itertools.islice(color_iter, n_traces))
        
        if vis_type == 'v':
            fig, axes = plt.subplots(1, n_groups, figsize=(figsize[0]*n_groups, figsize[1]), sharey=True)
        else:
            fig, axes = plt.subplots(n_groups, 1, figsize=(figsize[0], figsize[1]*n_groups), sharey=True)
            
        if n_groups == 1:
            axes = [axes]
    
        for i, traces in enumerate(data_groups):
            ax = axes[i]
            for j, trace in enumerate(traces):
                label = legends[j] if legends else f'Trace {j+1}'
                if vis_type == 'v':
                    ax.plot(trace, time, line_styles[j], color=color_list[j], label=label)
                    y_axis_label = "Time (ms)"
                    ax.set_xlabel("Amplitude", **self.config.label_style)
                else:
                    ax.plot(time, trace, line_styles[j], color=color_list[j], label=label)
                    x_axis_label = "Time (ms)"
                    ax.set_ylabel("Amplitude", **self.config.label_style)

            if titles:
                ax.set_title(titles[i], **self.config.title_style)
                
            if vis_type == 'v':    
                ax.margins(x=0.05, y=0)
            else:
                ax.margins(x=0, y=0.05)
            
            if vis_type == 'v':
                ax.invert_yaxis()
                
            if i == 0 and vis_type == 'v':
                ax.set_ylabel(y_axis_label, **self.config.label_style)
                
            if i == n_groups - 1 and vis_type != 'v':
                ax.set_xlabel(x_axis_label, **self.config.label_style)
        
            ax.legend(loc='upper right', fontsize=self.config.legend_fontsize)
    
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=self.config.figure_dpi)
        plt.show()

