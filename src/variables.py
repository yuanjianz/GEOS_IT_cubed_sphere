import sys
import os
import re
import xarray as xr
from datetime import datetime, timedelta, time
from process import Collection


def A1(date_to_process, raw_data_dir, output_dir):
    collection_A1 = Collection("A1", timedelta(hours=1), time(hour=0, minute=30))
    variable_map = {
        "rad_tavg_1hr_glo_C180x180x6_slv": ["ALBEDO", "CLDTOT", "LWGNT", "SWGDN"],
        "flx_tavg_1hr_glo_C180x180x6_slv": [
            "EFLUX",
            "EVAP",
            "FRSEAICE",
            "HFLUX",
            "PBLH",
            "PRECANV",
            "PRECCON",
            "PRECLSC",
            "PRECSNO",
            "PRECTOT",
            "USTAR",
            "Z0M",
        ],
        "lnd_tavg_1hr_glo_C180x180x6_slv": [
            "FRSNO",
            "GRN",
            "GWETROOT",
            "GWETTOP",
            "LAI",
            "PARDF",
            "PARDR",
            "SNODP",
            "SNOMAS",
        ],
        "slv_tavg_1hr_glo_C180x180x6_slv": [
            "QV2M",
            "SLP",
            "TO3",
            "TROPPT",
            "TS",
            "T2M",
            "U10M",
            "V10M",
        ],
    }

    def A1_compute(ds):
        if 'FRSEAICE' in ds:
            # Initialize SEAICE00 to SEAICE90 as zeros and set attributes
            for i in range(10):
                var_name = f'SEAICE{i*10:02}'
                ds[var_name] = xr.zeros_like(ds['FRSEAICE'])
                ds[var_name].attrs[
                    'long_name'
                ] = f'Fraction of grid box that has {i*10}-{(i+1)*10}% sea ice coverage'
                ds[var_name].attrs['units'] = '1'

            # Populate SEAICE00 to SEAICE90 based on the FRSEAICE value
            ds['SEAICE00'] = xr.where(ds['FRSEAICE'] < 0.1, 1, 0)
            ds['SEAICE10'] = xr.where(
                (ds['FRSEAICE'] >= 0.1) & (ds['FRSEAICE'] < 0.2), 1, 0
            )
            ds['SEAICE20'] = xr.where(
                (ds['FRSEAICE'] >= 0.2) & (ds['FRSEAICE'] < 0.3), 1, 0
            )
            ds['SEAICE30'] = xr.where(
                (ds['FRSEAICE'] >= 0.3) & (ds['FRSEAICE'] < 0.4), 1, 0
            )
            ds['SEAICE40'] = xr.where(
                (ds['FRSEAICE'] >= 0.4) & (ds['FRSEAICE'] < 0.5), 1, 0
            )
            ds['SEAICE50'] = xr.where(
                (ds['FRSEAICE'] >= 0.5) & (ds['FRSEAICE'] < 0.6), 1, 0
            )
            ds['SEAICE60'] = xr.where(
                (ds['FRSEAICE'] >= 0.6) & (ds['FRSEAICE'] < 0.7), 1, 0
            )
            ds['SEAICE70'] = xr.where(
                (ds['FRSEAICE'] >= 0.7) & (ds['FRSEAICE'] < 0.8), 1, 0
            )
            ds['SEAICE80'] = xr.where(
                (ds['FRSEAICE'] >= 0.8) & (ds['FRSEAICE'] < 0.9), 1, 0
            )
            ds['SEAICE90'] = xr.where(ds['FRSEAICE'] >= 0.9, 1, 0)

        # Scale 'SLP' and 'TROPPT' by 0.01
        if 'SLP' in ds:
            ds['SLP'] = ds['SLP'] * 0.01
            ds['SLP'].attrs['units'] = 'hPa'

        if 'TROPPT' in ds:
            ds['TROPPT'] = ds['TROPPT'] * 0.01
            ds['TROPPT'].attrs['units'] = 'hPa'

        return ds

    collection_A1.process_files_for_date(
        raw_data_dir, variable_map, date_to_process, output_dir, A1_compute
    )


def A3cld(date_to_process, raw_data_dir, output_dir):
    collection_A3cld = Collection("A3cld", timedelta(hours=3), time(hour=1, minute=30))
    variable_map = {
        "cld_tavg_3hr_glo_C180x180x6_v72": ["CFAN", "CFCU", "CFLS", "TAUCLI", "TAUCLW"],
        "rad_tavg_3hr_glo_C180x180x6_v72": ["CLOUD"],
        "asm_tavg_3hr_glo_C180x180x6_v72": ["QI", "QL"],
    }

    def A3cld_compute(ds):
        if 'TAUCLI' in ds and 'TAUCLW' in ds:
            ds['OPTDEPTH'] = ds['TAUCLI'] + ds['TAUCLW']
            ds['OPTDEPTH'].attrs['long_name'] = 'Optical Depth'
            ds['OPTDEPTH'].attrs['units'] = ds['TAUCLI'].attrs.get('units', 'unknown')
        return ds

    collection_A3cld.process_files_for_date(
        raw_data_dir, variable_map, date_to_process, output_dir, A3cld_compute
    )


def A3mstC(date_to_process, raw_data_dir, output_dir):
    collection_A3mstC = Collection(
        "A3mstC", timedelta(hours=3), time(hour=1, minute=30)
    )
    variable_map = {
        "mst_tavg_3hr_glo_C180x180x6_v72": [
            "DQRCU",
            "DQRLSAN",
            "REEVAPCN",
            "REEVAPLSAN",
        ]
    }

    def A3mstC_rename(ds):
        if 'REEVAPLSAN' in ds:
            ds = ds.rename({'REEVAPLSAN': 'REEVAPLS'})
        return ds

    collection_A3mstC.process_files_for_date(
        raw_data_dir, variable_map, date_to_process, output_dir, A3mstC_rename
    )


def A3mstE(date_to_process, raw_data_dir, output_dir):
    collection_A3mstE = Collection(
        "A3mstE", timedelta(hours=3), time(hour=1, minute=30)
    )
    variable_map = {
        "mst_tavg_3hr_glo_C180x180x6_v73": [
            "CMFMC",
            "PFICU",
            "PFILSAN",
            "PFLCU",
            "PFLLSAN",
        ]
    }
    collection_A3mstE.process_files_for_date(
        raw_data_dir, variable_map, date_to_process, output_dir
    )


def A3dyn(date_to_process, raw_data_dir, output_dir):
    collection_A3dyn = Collection("A3dyn", timedelta(hours=3), time(hour=1, minute=30))
    variable_map = {
        "cld_tavg_3hr_glo_C180x180x6_v72": ["DTRAIN"],
        "asm_tavg_3hr_glo_C180x180x6_v72": ["OMEGA", "RH", "U", "V"],
    }
    collection_A3dyn.process_files_for_date(
        raw_data_dir, variable_map, date_to_process, output_dir
    )


def I3(date_to_process, raw_data_dir, output_dir):
    collection_I3 = Collection("I3", timedelta(hours=3), time(hour=0, minute=0))
    variable_map = {"asm_inst_3hr_glo_C180x180x6_v72": ["PS", "QV", "T"]}

    def I3_compute(ds):
        # Scale 'PS' by 0.01
        if 'PS' in ds:
            ds['PS'] = ds['PS'] * 0.01
            ds['PS'].attrs['units'] = 'hPa'

        return ds

    collection_I3.process_files_for_date(
        raw_data_dir, variable_map, date_to_process, output_dir, I3_compute
    )


def CN(raw_data_dir, output_dir):
    collection_CN = Collection("CN", timedelta(hours=0), time(hour=12, minute=0))
    variable_map = {
        "asm_const_0hr_glo_C180x180x6_slv": [
            "FRLAKE",
            "FRLAND",
            "FRLANDICE",
            "FROCEAN",
            "PHIS",
        ]
    }

    date_to_process = datetime.strptime("19980101", "%Y%m%d").date()
    pattern = r"/\d{4}/\d{2}/\d{2}"
    raw_data_dir = re.sub(pattern, "/1998/01/01", raw_data_dir)
    pattern = r"/\d{4}/\d{2}"
    output_dir = re.sub(pattern, "/1998/01", output_dir)

    if not os.path.exists(raw_data_dir):
        print("Invalid Raw Data Directory!")
        sys.exit(2)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    collection_CN.process_files_for_date(
        raw_data_dir, variable_map, date_to_process, output_dir
    )


def CTM_A1(date_to_process, raw_data_dir, output_dir):
    collection_CTM_A1 = Collection(
        "CTM_A1", timedelta(hours=1), time(hour=0, minute=30)
    )
    variable_map = {"tavg_1hr_ctm_c0720_v72": ["CX", "CY", "DELP", "MFXC", "MFYC"]}

    def CTM_A1_compute(ds):
        # Scale 'PS' by 0.01
        # if 'PS' in ds:
        #    ds['PS'] = ds['PS'] * 0.01
        #    ds['PS'].attrs['units'] = 'hPa'

        return ds

    collection_CTM_A1.process_files_for_date(
        raw_data_dir, variable_map, date_to_process, output_dir, CTM_A1_compute
    )


def CTM_I1(date_to_process, raw_data_dir, output_dir):
    collection_CTM_I1 = Collection("CTM_I1", timedelta(hours=1), time(hour=0, minute=0))
    variable_map = {"inst_1hr_ctm_c0720_v72": ["PS", "QV"]}

    def CTM_I1_compute(ds):
        # Scale 'PS' by 0.01
        if 'PS' in ds:
            ds['PS'] = ds['PS'] * 0.01
            ds['PS'].attrs['units'] = 'hPa'

        return ds

    collection_CTM_I1.process_files_for_date(
        raw_data_dir, variable_map, date_to_process, output_dir, CTM_I1_compute
    )
