import json
from pathlib import Path
import polars as pl
from typing import Union


def load_txt_as_json(filepath: str) -> list:
    return json.load(open(filepath, "r"))


def find_files_with_extension(
        directory: Union[str, Path], 
        extension: str
    ) -> list:
    path = Path(directory)
    
    # Check if the directory exists
    if not path.exists() or not path.is_dir():
        print(f"Error: The directory {directory} does not exist.")
        return []
    
    pattern = f"*.{extension}"
    return list(path.glob(pattern))


def load_txt_to_list_json(input_directory: str,
                          file_ext: str = "txt") -> list:
    json_files_dir = input_directory
    txt_files = find_files_with_extension(
        directory=json_files_dir,
        extension=file_ext)
    
    json_files = []
    for t in txt_files:
        list_of_jsons = load_txt_as_json(t)
        json_files.extend(list_of_jsons)

    return json_files


def filter_by_quantile(
        df: pl.DataFrame,
        col: str,
        lower_bound: float,
        interp: str = "nearest"
    ) -> pl.DataFrame:
    df = df.filter(
        pl.col(col) > df[col].quantile(lower_bound, interp)
    )
    return df
