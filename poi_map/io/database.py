from pathlib import Path
import pandas as pd
import dash_leaflet as dl


def get_data(file: Path) -> pd.DataFrame:
    df = pd.read_parquet(file)
    return df
