from pathlib import Path
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Literal, Self


LogLevel = Literal["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class POIMapConfig(BaseModel):
    title: str = Field(..., description="Title of the app.")
    database: Path = Field(..., description="Path to the database file.")
    assets: Path = Field(..., description="Path to the assets folder.")
    categories: list[str] = Field(
        ...,
        description="List of POI categories to use. Each category must have an SVG icon with the same name in the assets folder.",
    )
    loglevel: LogLevel = Field(
        "INFO", description="Level at which message should be logged.."
    )

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

    @field_validator("assets")
    @classmethod
    def assets_must_exist(cls, v: Path) -> Path:
        if not v.exists():
            raise ValueError("Assets directory does not exist.")
        return v

    @model_validator(mode="after")
    def categories_must_have_assets(self) -> Self:
        for category in self.categories:
            if not (self.assets / f"{category}.svg").exists():
                raise ValueError(f"Icon for category '{category}' does not exist.")
        return self
