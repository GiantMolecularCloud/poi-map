import dash_bootstrap_components as dbc
from dash import html, Dash, Input, Output, callback
import dash_leaflet as dl
import pandas as pd

from ..config.models import POIMapConfig
from ..io.database import get_data


class POIMapApp:
    def __init__(
        self,
        config: POIMapConfig,
    ) -> None:
        self.config = config

        self.df = get_data(config.database)

        self.app = Dash(
            __name__,
            title=self.config.title,
            external_stylesheets=[dbc.themes.DARKLY],
            assets_folder="../assets",
        )
        self._init_callbacks()

    def _init_callbacks(self) -> None:
        self.app.callback(
            Output(component_id="map", component_property="children"),
            Input(component_id="category-filter", component_property="value"),
        )(self._update_markers)

    def _build_category_filter(self) -> html.Div:
        return html.Div(
            [
                dbc.Checklist(
                    options=self.config.categories,
                    value=self.config.categories,
                    id="category-filter",
                    switch=True,
                ),
            ]
        )

    def _get_markers(self, df: pd.DataFrame) -> dl.FeatureGroup:
        return dl.FeatureGroup(
            [
                dl.Marker(
                    position=[row.latitude, row.longitude],
                    children=[dl.Tooltip(content=", ".join(row.category))],
                )
                for _, row in df.iterrows()
            ]
        )

    def _update_markers(self, input_value):
        selected = self.df[
            self.df.category.apply(
                lambda category: any(x in category for x in input_value)
            )
        ]
        markers = self._get_markers(selected)
        return self._build_map(markers)

    def _get_statistics(self) -> dbc.Table:
        return dbc.Table.from_dataframe(
            pd.DataFrame(self.df.category.explode().value_counts()).reset_index(),
            striped=True,
            bordered=False,
            hover=True,
        )

    def _build_sidebar(self) -> None:
        self.sidebar = html.Div(
            [
                html.H1(self.config.title),
                html.Div(
                    [
                        html.Hr(),
                        html.H3("Categories"),
                        self._build_category_filter(),
                    ]
                ),
                html.Div(
                    [
                        html.Hr(),
                        html.H3("Add new POI"),
                        html.P("Buttons and stuff to add a new POI."),
                    ]
                ),
                html.Hr(),
                html.Div(
                    [
                        html.Hr(),
                        html.H3("Statistics"),
                        self._get_statistics(),
                    ],
                    className="bottom",
                ),
            ],
            className="sidebar",
        )

    def _build_map_controls(self) -> dl.FeatureGroup:
        edit_control = dl.EditControl(
            draw=dict(
                marker=True,
                circle=False,
                circlemarker=False,
                polyline=False,
                polygon=False,
                rectangle=False,
            )
        )
        locate_control = dl.LocateControl(locateOptions={"enableHighAccuracy": True})
        scale_control = dl.ScaleControl(position="bottomleft")

        return dl.FeatureGroup([edit_control, locate_control, scale_control])

    def _build_map(self, markers) -> None:
        return [
            dl.TileLayer(),
            markers,
            self._build_map_controls(),
        ]

    def _build_content(self) -> None:
        self.content = html.Div(
            [
                dl.Map(
                    center=[56, 10],
                    zoom=6,
                    style={"height": "100vh"},
                    children=self._build_map(self._get_markers(self.df)),
                    id="map",
                ),
            ],
            id="main",
            className="main",
        )

    def build(self) -> None:
        self._build_sidebar()
        self._build_content()
        self.app.layout = html.Div([self.sidebar, self.content])

    def run(self) -> None:
        self.app.run(debug=True if self.config.loglevel == "DEBUG" else False)


# ToDo: add callback to "add marker" button: open modal with form for POI details
# ToDo: convert df to geopandas df and use GeoJSON to display markers
# ToDo: add further information to markers (e.g. description)
# ToDo: refactor
