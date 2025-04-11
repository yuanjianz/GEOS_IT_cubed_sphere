import xarray as xr
import os
import sys
from datetime import datetime, timedelta
from attribute import change_attrs
from compress import compress_and_chunk_encoding


class Collection:
    def __init__(self, processed_collection, time_frequency, time_offset):
        self.processed_collection = processed_collection
        self.time_frequency = time_frequency
        self.time_offset = time_offset

    def concatenate_daily_files(self, datasets, date, output_dir, attr_func=None):
        """
        Concatenate multiple hourly files into a single daily file.
        """
        try:
            combined = xr.concat(datasets, dim="time")

            # Sort variables alphabetically
            sorted_variables = sorted(combined.data_vars)
            combined = combined[sorted_variables]

            # Reverse the 'lev' dimension to make it vertical up
            if 'lev' in combined.dims:
                reversed_data = combined.isel(lev=slice(None, None, -1))
                combined = reversed_data.assign_coords(lev=combined.lev)

            # Create the output file path
            daily_filename = (
                f"GEOSIT.{date.strftime('%Y%m%d')}.{self.processed_collection}.C180.nc"
            )
            daily_file_path = os.path.join(output_dir, daily_filename)

            # Change attributes
            if attr_func:
                attr_func(combined, daily_filename)
            else:
                change_attrs(combined, daily_filename, self.processed_collection)

            encoding = compress_and_chunk_encoding(combined)
            combined.to_netcdf(daily_file_path, encoding=encoding)
            print(f"Daily file saved to {daily_file_path}")
            return daily_file_path
        except Exception as e:
            print(f"An error occurred while concatenating files: {e}", file=sys.stderr)

    def process_files_for_date(
        self, directory, variable_map, date, output_dir, compute_func=None
    ):
        """
        Process all files in a directory for a given collection and date.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        current_time = datetime.combine(date, self.time_offset)
        end_time = current_time + timedelta(days=1)

        datasets = []

        while current_time < end_time:
            time_str = current_time.strftime('%Y-%m-%dT%H%M')
            temp_datasets = []

            for collection_name, variables in variable_map.items():

                filename = f"GEOS.it.asm.{collection_name}.GEOS5294.{time_str}.V01.nc4"
                file_path = os.path.join(directory, filename)

                if os.path.exists(file_path):
                    try:
                        ds = xr.open_dataset(file_path)
                        # Select the specific variables
                        selected_vars = ds[variables]

                        # Perform custom computations if a compute function is provided
                        if compute_func:
                            selected_vars = compute_func(selected_vars)

                        temp_datasets.append(selected_vars)

                    except Exception as e:
                        print(
                            f"Error: Could not open {file_path}. It might be corrupted or invalid.",
                            file=sys.stderr,
                        )
                        return
                        # print(f"Details: {e}", file=sys.stderr)

                else:
                    print(f"File {file_path} does not exist.", file=sys.stderr)
                    return

            if temp_datasets:
                # Merge the datasets for this current time step
                merged_dataset = xr.merge(temp_datasets)
                datasets.append(merged_dataset)

            current_time += self.time_frequency

        if datasets:
            return self.concatenate_daily_files(datasets, date, output_dir)
