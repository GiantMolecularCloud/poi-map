import logging
from typing import Sequence
import pprint

import dash_bootstrap_components as dbc
from dash import html, Dash
import dash_leaflet as dl

from .parser import parse_config
from ..io.database import get_data

log = logging.getLogger(__name__)


def main(argv: Sequence[str] | None = None) -> None:
    
    config = parse_config(argv)

    logging.basicConfig(
        format="[%(asctime)s] [%(levelname)8s] --- %(message)s",
        level=config.loglevel,
    )
    
    log.info("-" * 50)
    log.info("Config successfully parsed.")
    for line in pprint.pformat(config).split(", "):
        log.info(line)
    log.info("-" * 50)
    
    
    df = get_data(config.database)
    
    markers = dl.FeatureGroup(
        [dl.Marker(position=[row.latitude, row.longitude]) for _,row in df.iterrows()]
    )
    
     


    app = Dash(external_stylesheets=[dbc.themes.DARKLY])

    # the style arguments for the sidebar. We use position:fixed and a fixed width
    SIDEBAR_STYLE = {
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "24rem",
        "padding": "1rem",
    }

    # the styles for the main content position it to the right of the sidebar and
    # add some padding.
    CONTENT_STYLE = {
        "margin-left": "24rem",
    }

    sidebar = html.Div(
        [
            html.H1(config.title),
            html.Hr(),
            html.H3("Categories"),
            html.P("Select categories to show on the map."),
            html.Hr(),
            html.H3("Add new POI"),
            html.P("Buttons and stuff to add a new POI."),
            html.Hr(),
        ],
        style=SIDEBAR_STYLE,
    )

    content = html.Div(
        [
            dl.Map(
                center=[56,10], 
                zoom=6, 
                style={'height': '100vh'}, 
                children=[
                    dl.TileLayer(),
                    markers,
                    dl.FeatureGroup(
                        [
                            dl.EditControl(draw=dict(
                                marker=True, circle=False, circlemarker=False, polyline=False, polygon=False, rectangle=False
                                )
                            ),
                            dl.LocateControl(locateOptions={'enableHighAccuracy': True}),
                            dl.ScaleControl(position="bottomleft"),
                        ],
                    ),
                ],
            ),
        ], 
        id="page-content", 
        style=CONTENT_STYLE
    )

    app.layout = html.Div([sidebar, content])
    
    # ToDo: add callback to "add marker" button: open modal with form for POI details
    # ToDo: convert df to geopandas df and use GeoJSON to display markers
    # ToDo: add further information to markers (e.g. description)
    # ToDo: add category filter
    # ToDo: refactor and move dash app to separate module

    
    app.run(debug=True if config.loglevel == "DEBUG" else False)