import json
from pathlib import Path
import polars as pl
from typing import Union


def is_instance_initialized(instance):
    return bool(instance.__dict__)


def load_txt_as_json(filepath: str) -> list:
    return json.load(open(filepath, "r"))


def to_json(file_list: list) -> list:
    file_list_json = [load_json_file(f) for f in file_list]
    file_list_json = [element for sublist in file_list_json for element in sublist]
    return file_list_json
    

def number_of_samples(json_data: list) -> int:
    return len(json_data)


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


def search_listdict_by_keys(
        list_of_dicts: list[dict],
        values_to_match: list[str],
        keys_to_search: list[str] = ["MRN", "SpecimenCollectionDate"]
    ) -> str:
    # values_to_match = ["2235965", "2024-10-04T10:37:00"]
    filtered_data = []
    for dictionary in list_of_dicts:
        match = True
        for key, value in zip(keys_to_search, values_to_match):
            if dictionary[key] != value:
                match = False
                break
        if match:
            filtered_data.append(dictionary)
    
    if len(filtered_data) == 0:
        return "Flow cytometry report is not available."
    else:
        return filtered_data[0]["Intepretation"]
