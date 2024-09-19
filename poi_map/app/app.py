import base64

import dash_bootstrap_components as dbc
from dash import html, Dash
import dash_leaflet as dl

from ..config.models import POIMapConfig


class POIMapApp:
    def __init__(
        self,
        config: POIMapConfig,
    ) -> None:
        self.config = config

        self.app = Dash(
            __name__,
            title=self.config.title,
            external_stylesheets=[dbc.themes.DARKLY],
            assets_folder="../assets",
        )

        # the style arguments for the sidebar. We use position:fixed and a fixed width
        self.SIDEBAR_STYLE = {
            "position": "fixed",
            "top": 0,
            "left": 0,
            "bottom": 0,
            "width": "24rem",
            "padding": "1rem",
        }

        # the styles for the main content position it to the right of the sidebar and
        # add some padding.
        self.CONTENT_STYLE = {
            "margin-left": "24rem",
        }

    def _get_button(self, category: str) -> html.Button:
        with open(self.config.assets / f"{category}.svg", "r") as f:
            im = f.read()
        im = im.replace('fill="#000000"', 'fill="#FFFFFF"')
        encoded = base64.b64encode(str.encode(im))
        svg = f"data:image/svg+xml;base64,{encoded.decode()}"

        return html.Button(
            id=category,
            children=[
                html.Div(
                    [
                        html.ObjectEl(
                            data=svg,
                            width=20,
                            height=20,
                            className="button-icon filter-on",
                        ),
                        html.P(category.capitalize(), className="button-text"),
                    ],
                )
            ],
            className="filter-button",
        )

    def _build_sidebar(self) -> None:
        self.sidebar = html.Div(
            [
                html.H1(self.config.title),
                html.Hr(),
                html.H3("Categories"),
                html.P("Select categories to show on the map."),
                self._get_button("city"),
                html.Br(),
                self._get_button("sea"),
                html.Hr(),
                html.H3("Add new POI"),
                html.P("Buttons and stuff to add a new POI."),
                html.Hr(),
            ],
            style=self.SIDEBAR_STYLE,
        )

    def _build_content(
        self,
        markers: dl.FeatureGroup,
    ) -> None:
        self.content = html.Div(
            [
                dl.Map(
                    center=[56, 10],
                    zoom=6,
                    style={"height": "100vh"},
                    children=[
                        dl.TileLayer(),
                        markers,
                        dl.FeatureGroup(
                            [
                                dl.EditControl(
                                    draw=dict(
                                        marker=True,
                                        circle=False,
                                        circlemarker=False,
                                        polyline=False,
                                        polygon=False,
                                        rectangle=False,
                                    )
                                ),
                                dl.LocateControl(
                                    locateOptions={"enableHighAccuracy": True}
                                ),
                                dl.ScaleControl(position="bottomleft"),
                            ],
                        ),
                    ],
                ),
            ],
            id="page-content",
            style=self.CONTENT_STYLE,
        )

    def build(self, markers: dl.FeatureGroup) -> None:
        self._build_sidebar()
        self._build_content(markers)
        self.app.layout = html.Div([self.sidebar, self.content])

    def run(self) -> None:
        self.app.run(debug=True if self.config.loglevel == "DEBUG" else False)


# ToDo: add callback to "add marker" button: open modal with form for POI details
# ToDo: convert df to geopandas df and use GeoJSON to display markers
# ToDo: add further information to markers (e.g. description)
# ToDo: add category filter
# ToDo: refactor and move dash app to separate module
