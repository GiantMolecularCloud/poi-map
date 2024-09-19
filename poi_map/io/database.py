from pathlib import Path
import pandas as pd
import dash_leaflet as dl


def get_data(file: Path) -> pd.DataFrame:
    df = pd.read_parquet(file)
    return df


def get_markers(df: pd.DataFrame) -> dl.FeatureGroup:
    return dl.FeatureGroup(
        [dl.Marker(position=[row.latitude, row.longitude]) for _, row in df.iterrows()]
    )
