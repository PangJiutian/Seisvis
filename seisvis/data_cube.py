# Copyright (c) 2025 Qi Pang.
# All rights reserved.

import numpy as np

class DataCube:
    def __init__(self):
        self.data = {
            'seismic': {},     # seismic data, eg: {'10 degree': ndarray, '20 degree': ndarray}
            'properties': {},  # properties, eg: {'PHIE': ndarray, 'VCL': ndarray}
            'horizons': {},    # horizons, eg: {'Top': ndarray}
            'wells': {}        # wells, eg: {'Well-A': {'log': ndarray, 'coord': (inline, xline)}}
        }

    def add_seismic(self, name, data):
        self.data['seismic'][name] = data

    def add_property(self, name, data):
        self.data['properties'][name] = data

    def add_horizon(self, name, data):
        self.data['horizons'][name] = data
    
    # need to be updated to {'Well-A': {'log': df(all properties not one), 'coord': (inline, xline)}}
    def add_well(self, well_name, data):  
        self.data['wells'][well_name] = data
    
    def remove(self, category, name):
        if category in self.data:
            self.data[category].pop(name, None)

    def get(self, category, name=None):
        category_data = self.data.get(category, {}) 
        if name is None:
            return category_data
        if isinstance(name, list):
            return {n: category_data.get(n, None) for n in name}
        # name is a single string
        return category_data.get(name, None)
    
    def get_dim(self, category, name):
        arr = self.get(category, name)
        if isinstance(arr, np.ndarray):
            return arr.ndim
        return None
    
    def summary(self):
        print("DataCube Information:")
        for category, content in self.data.items():
            print(f"- {category}: {list(content.keys())}")
