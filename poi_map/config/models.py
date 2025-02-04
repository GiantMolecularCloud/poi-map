from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

LogLevel = Literal["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class POIMapConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., description="Title of the app.")
    database: Path = Field(..., description="Path to the database file.")
    categories: list[str] = Field(..., description="List of POI categories to use.")
    zoomlevel: int = Field(5, description="Initial zoom level.")
    port: int = Field(8080, description="Port to run the app on.")
    loglevel: LogLevel = Field("INFO", description="Level at which messages should be logged.")

    @field_validator("database")
    @classmethod
    def database_must_exist(cls, v: Path) -> Path:
        if not v.exists():
            raise ValueError("Database file does not exist.")
        return v

    @field_validator("database")
    @classmethod
    def database_must_be_parquet(cls, v: Path) -> Path:
        if v.suffix != ".parquet":
            raise ValueError("Database file must be a .parquet file.")
        return v
