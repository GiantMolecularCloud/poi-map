from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from typing import Literal


LogLevel = Literal["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

class POIMapConfig(BaseModel):
    title: str = Field(..., description="Title of the app.")
    database: Path = Field(..., description="Path to the database file.")
    categories: dict[str, Path | None] = Field(..., description="Dictionary of POI categories and corresponding icons. Leave value as None to use default icon.")
    loglevel: LogLevel = Field("INFO", description="Level at which message should be logged..")
    
    @field_validator("database")
    @classmethod
    def database_must_exist(cls, v: Path) -> Path:
        if not v.exists():
            raise ValueError("Database file does not exist.")
        return v
    
    @field_validator("database")
    @classmethod
    def database_must_be_sqlite(cls, v: Path) -> Path:
        if v.suffix != ".parquet":
            raise ValueError("Database file must be a Parquet file.")
        return v
    
    @field_validator("categories")
    @classmethod
    def category_icons_must_exist(cls, v: dict[str, Path | None]) -> dict[str, Path | None]:
        for category, icon in v.items():
            if icon is not None and not icon.exists():
                raise ValueError(f"Icon for category '{category}' does not exist.")
        return v