from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pandera as pa
from pandera.typing import Series


def get_data(file: Path) -> pd.DataFrame:
    if file.exists():
        df = pd.read_parquet(file)
        return POIData.validate(df)
    else:
        return initialize_schema(POIData)  # type:ignore[arg-type]


def initialize_schema(model: pa.DataFrameModel) -> pd.DataFrame:
    schema = model.to_schema()
    return pd.DataFrame(columns=list(schema.columns.keys())).astype(
        {column_name: column_type.dtype.type.name for column_name, column_type in schema.columns.items()}
    )


class POIData(pa.DataFrameModel):
    latitude: Series[float] = pa.Field(ge=-90.0, le=90.0, title="Latitude", description="Latitude of the POI.")
    longitude: Series[float] = pa.Field(ge=-180.0, le=180.0, title="Longitude", description="Longitude of the POI.")
    category: Series = pa.Field(title="Category", description="One or more categories that the POI falls into.")
    date: Series[date] = pa.Field(title="Date", description="Date of the POI.")
    title: Series[str] = pa.Field(title="Title", description="Title of the POI.")
    description: Series[str] = pa.Field(title="Description", description="Description of the POI.")

    @pa.check("category")
    @classmethod
    def category_must_be_list(cls, series: Series) -> Series[bool]:
        """Ensure that the category column is a list of strings."""
        return series.apply(lambda x: isinstance(x, np.ndarray) and all(isinstance(i, str) for i in x))
