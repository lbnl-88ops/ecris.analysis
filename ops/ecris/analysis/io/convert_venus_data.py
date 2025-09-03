# This module processes VENUS database files and packages them as
# compressed packages.

import polars as pl
import sqlite3
import numpy as np
from datetime import datetime
import shutil
from pathlib import Path
from typing import List

TIME_NAME = "unix_epoch_milliseconds"

RENAME_DICT = {
    'bl_robin_i': 'robin_i',
    'fifty_k_cond_bar_NW': 'fifty_k_cond_bar_nw',
    'fifty_k_cond_bar_NE': 'fifty_k_cond_bar_ne',
    'bl_mig2_mbar': 'bl_mig2_torr',
    'LHe_level_in': 'LHe_level_percent',
    'unix_epoch_microseconds': TIME_NAME
}

def get_table_names(file):
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    return pl.read_database_uri(query=query, uri=f"sqlite://{file}")["name"]

def read_column_names(files: List[Path], rename_map=RENAME_DICT):
    all_columns = {}
    for file in files:
        if file.suffix == ".db":
            table_names = get_table_names(file)
            with sqlite3.connect(file) as conn:
                cursor = conn.cursor()
                column_names = set()
                for k in table_names:
                    cursor.execute(f"PRAGMA table_info({k});")
                    column_names.update(
                        set(
                            map(lambda x: x[1], cursor.fetchall())
                        )
                    )
                cursor.close()
            for k, v in rename_map.items():
                if k in column_names:
                    column_names.remove(k)
                    column_names.add(v)
            all_columns[file] = column_names
    return all_columns

def union_of_column_names(files: List[Path], rename_map=RENAME_DICT):
    all_columns = read_column_names(files, rename_map=rename_map)
    return set.union(*all_columns.values())

def all_unique_column_names(files: List[Path]):
    all_columns = read_column_names(files, rename_map={})
    intersect = set.intersection(*all_columns.values())
    all_unique = {}
    for f, s in all_columns.items():
        all_unique[f] = s - intersect
    return all_unique

def read_full_db(file_name):
    table_names = get_table_names(file_name)
    dfs = []
    for name in table_names:
        query = f"SELECT * FROM {name}"
        dfs.append(
            pl.read_database_uri(query=query, uri=f"sqlite://{file_name}")
        )
    df = pl.concat(dfs, how="align")
    for k, v in RENAME_DICT.items():
        if k in df:
            df = df.rename({k: v})
    return df.sort(by=TIME_NAME)

def write_chunked(output: Path, df, interval="1d"):
    output.mkdir(exist_ok=True)
    start_time = datetime.fromtimestamp(float(df[TIME_NAME].min()) / 1000)
    stop_time = datetime.fromtimestamp(float(df[TIME_NAME].max()) / 1000)
    print(start_time, stop_time)
    time_chunks = pl.datetime_range(start_time, stop_time, interval="1d", eager=True)
    for start, stop in zip(time_chunks[:-1], time_chunks[1:]):
        selection = df.filter(
            (pl.col(TIME_NAME) > int(start.timestamp() * 1000)) & (pl.col(TIME_NAME) <= int(stop.timestamp() * 1000))
        )
        if not selection.is_empty():
            selection.write_parquet(
                output / f"venus_data_{start.strftime('%Y_%m_%d_%H_%M_%S')}.parquet")
        else:
            print(f"WARNING: Selection {start} to {stop} is empty")
    return time_chunks

def convert_venus_db_files(files: List[Path], output_path=Path("./data/venus"), 
                           *, overwrite = False):
    column_names = union_of_column_names(files)
    column_names.add("time")
    skipped = 0
    failed = 0
    print(f"Converting {len(files)} files...")
    output_path.mkdir(exist_ok=True)
    for file in files:
        if file.suffix == '.db':
            try:
                filename = output_path / (file.stem + '.parquet')
                if not overwrite and filename.exists():
                    print(f"Skipping file, converted file {filename} already exists")
                    skipped += 1
                    continue
                df = read_full_db(file)
                df = df.with_columns(time=pl.col(TIME_NAME).cast(pl.Float64) * 1e-3)
                for k in column_names:
                    if k not in df:
                        df = df.with_columns(pl.lit(np.nan).alias(k))
                        print(f"WARNING: Adding column {k}")
                for k in df.columns:
                    if k not in column_names:
                        df = df.drop(k)
                        print(f"WARNING: Removing column {k}")
                df.write_parquet(filename)
            except BaseException as e:
                print(f"Conversion failed: {e}")
                failed += 1
    print("File conversion complete." + (f" Skipped: {skipped}/{len(files)}." if skipped else "")
          + (f" Failed: {failed}/{len(files)}." if failed else ""))

def convert_directory(files: List[Path], output_path=Path("./data_full"), interval="1d"):
    all_times = []
    column_names = union_of_column_names(files)
    column_names.add("time")
    print("Normalizing to column_names:")
    print(column_names)
    if output_path.exists():
        shutil.rmtree(output_path)
    for file in files:
        if file.suffix == '.db':
            print(f"Reading {file}")
            df = read_full_db(file)
            df = df.with_columns(time=pl.col(TIME_NAME).cast(pl.Float64) * 1e-3)
            for k in column_names:
                if k not in df:
                    df = df.with_columns(pl.lit(np.nan).alias(k))
                    print(f"WARNING: Adding column {k}")
            for k in df.columns:
                if k not in column_names:
                    df = df.drop(k)
                    print(f"WARNING: Removing column {k}")
            time_chunks = write_chunked(output_path, df, interval=interval)
            all_times.append(time_chunks)
    return all_times