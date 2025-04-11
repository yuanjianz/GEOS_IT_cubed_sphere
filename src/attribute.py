import xarray as xr
import os
from datetime import datetime, timezone


class File_Attributes:
    def __init__(self, ds):
        self.ds = ds

    def inspect_attr(self):
        print("Global attributes:")
        for attr in self.ds.attrs:
            print(f"{attr}: {self.ds.attrs[attr]}")

        for var in self.ds.data_vars:
            print(f"\nAttributes for variable '{var}':")
            for attr in self.ds[var].attrs:
                print(f"  {attr}: {self.ds[var].attrs[attr]}")

    def add_global_attr(self, attr, value):
        self.ds.attrs[attr] = value

    def add_variable_attr(self, var, attr, value):
        self.ds[var].attrs[attr] = value

    def delete_global_attr(self, attr):
        if attr in self.ds.attrs:
            del self.ds.attrs[attr]

    def delete_variable_attr(self, var, attr):
        if attr in self.ds[var].attrs:
            del self.ds[var].attrs[attr]

    def clear_global_attr(self):
        self.ds.attrs.clear()

    def clear_variable_attr(self):
        for var in self.ds.variables:
            self.ds[var].attrs.clear()


def change_attrs(ds, file_name, collection_name):
    current_time = datetime.now(timezone.utc).strftime("%Y/%m/%d %H:%M:%S GMT+0000")
    attr = File_Attributes(ds)

    attr.clear_global_attr()

    attr.add_global_attr(
        "Title",
        f"GEOS-IT {collection_name} (cubed-sphere grid), processed for GEOS-Chem input",
    )
    attr.add_global_attr(
        "Contact", "GEOS-Chem Support Team (geos-chem-support@as.harvard.edu)"
    )
    attr.add_global_attr("References", "www.geos-chem.org")
    attr.add_global_attr("RangeEndingTime", "23:59:59.999999")
    attr.add_global_attr("Filename", file_name)
    attr.add_global_attr("History", f"File generated on: {current_time}")
    attr.add_global_attr("ProductionDateTime", current_time)
    attr.add_global_attr("Format", "NetCDF-4")
    attr.add_global_attr("Version", "GEOS_FP")
