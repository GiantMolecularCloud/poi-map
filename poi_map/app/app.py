import logging
from datetime import date, datetime
from typing import Any, Iterable

import dash_bootstrap_components as dbc
import dash_leaflet as dl
import numpy as np
import pandas as pd
from dash import Dash, Input, Output, State, dcc, html
from pydantic import ValidationError

from ..config.models import POIMapConfig
from ..io.database import POIData, get_data


class POIMapApp:
    def __init__(
        self,
        config: POIMapConfig,
    ) -> None:
        """
        Initialize the POI Map App.

        :param config: Configuration of the app.
        """
        self._log = logging.getLogger(__name__)
        self._log.setLevel(config.loglevel)

        self.config = config
        self.df = get_data(config.database)

        self.app = Dash(
            __name__,
            title=self.config.title,
            external_stylesheets=[dbc.themes.DARKLY],
            assets_folder="../assets",
        )
        self.init_callbacks()

    def init_callbacks(self) -> None:
        """
        Attach inital callbacks to the app.

        The following callbacks are attached:
        - filter_markers: Filter markers based on selected categories.
        """

        def filter_markers(
            filtered_categories: Iterable,
            start_date: str,
            end_date: str,
        ) -> list:
            """
            Filter markers based on selected categories and date range.

            :param filtered_categories: List of selected categories.
            :param start_date: Start date of the date range.
            :param end_date: End date of the date range.
            :return: Map with Tile Layer, markers and controls.
            """
            selected = self.df[self.df.category.apply(lambda category: any(x in category for x in filtered_categories))]

            if start_date is not None and end_date is not None:
                start_date_ = date.fromisoformat(start_date)
                end_date_ = date.fromisoformat(end_date)
                selected = selected[(selected.date >= start_date_) & (selected.date <= end_date_)]

            return self.build_map()

        self.app.callback(
            Output(component_id="map", component_property="children"),
            Input(component_id="category-filter", component_property="value"),
            Input(component_id="date-filter", component_property="start_date"),
            Input(component_id="date-filter", component_property="end_date"),
        )(filter_markers)

    def get_markers(self, df: pd.DataFrame) -> list[dict]:
        """
        Get a list of serialized marker data based on the DataFrame.

        :param df: DataFrame with POI data.
        :return: List of serialized marker data.
        """
        return [
            {
                "position": [row.latitude, row.longitude],
                "title": row.title,
                "date": row.date.isoformat(),
                "category": row.category,
                "description": row.description,
            }
            for _, row in df.iterrows()
        ]

    def get_statistics(self) -> dbc.Table:
        """
        Get statistics of the POI data.

        :return: Table with statistics.
        """
        return dbc.Table.from_dataframe(
            pd.DataFrame(self.df.category.explode().value_counts()).reset_index(),
            striped=True,
            bordered=False,
            hover=True,
        )

    def build_sidebar(self) -> None:
        """
        Build the sidebar of the app.
        """
        self.sidebar = html.Div(
            [
                html.H1(self.config.title),
                html.Hr(),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3("Categories"),
                                dbc.Checklist(
                                    options=self.config.categories,
                                    value=self.config.categories,
                                    id="category-filter",
                                    switch=True,
                                ),
                            ]
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                html.H3("Date Range"),
                                dcc.DatePickerRange(
                                    id="date-filter",
                                    initial_visible_month=date.today(),
                                ),
                            ]
                        ),
                    ]
                ),
                html.Hr(),
                html.Div(
                    [
                        html.Hr(),
                        html.H3("Statistics"),
                        self.get_statistics(),
                    ],
                    className="bottom",
                ),
            ],
            className="sidebar",
        )
        self.attach_new_poi_callbacks()
        self.attach_remove_poi_callbacks()

    def build_map_controls(self) -> dl.FeatureGroup:
        """
        Build a FeatureGroup of map controls.

        Enabled controls:
        - LocateControl: Locate the user (Brwoser asks for confirmation).
        - ScaleControl: Display a scale on the map.

        Disabled controls:
        - EditControl: Add, edit and remove markers.

        :return: FeatureGroup of map controls.
        """
        locate_control = dl.LocateControl(locateOptions={"enableHighAccuracy": True})
        scale_control = dl.ScaleControl(position="bottomleft")

        return dl.FeatureGroup([locate_control, scale_control])

    def build_map(self) -> list:
        """
        Build a map with markers and controls.

        :return: List of map components.
        """
        return [
            dl.TileLayer(),
            dl.FeatureGroup(
                id="map-markers", children=[self.format_marker(marker) for marker in self.get_markers(self.df)]
            ),
            self.build_map_controls(),
        ]

    def build_main(self) -> None:
        """
        Build the main part of the app (the map window).
        """
        self.content = html.Div(
            [
                html.Div(
                    id="controls",
                    children=[
                        dbc.Button(
                            "Add POI",
                            id="add-poi-modal-open",
                            disabled=False,
                        ),
                        dbc.Button(
                            "Remove POI",
                            id="remove-poi-modal-open",
                            disabled=False,
                            style={"margin-left": "1rem"},
                        ),
                    ],
                    className="main main-button",
                ),
                dl.Map(
                    center=[self.df.latitude.median(), self.df.longitude.median()],
                    zoom=self.config.zoomlevel,
                    style={"height": "100vh"},
                    children=self.build_map(),
                    id="map",
                ),
                html.Div(id="out"),
                html.Div(
                    id="user-response",
                    children=[
                        self.get_new_poi_modal(),
                        self.get_toast(message="Click on the map to add a POI.", id="add-poi-toast"),
                        self.get_success_message(message="POI added successfully.", id="new-poi-success"),
                        self.get_success_message(message="POI removed successfully.", id="remove-poi-success"),
                        self.get_remove_poi_modal(),
                    ],
                    className="main user-response",
                ),
            ],
            id="main",
            className="main",
        )

    def get_toast(
        self,
        message: str,
        id: str,
    ) -> dbc.Alert:
        """
        Get a preconfigured Alert primary message.

        :param message: Message displayed in the alert.
        :param id: ID of the alert.
        :return: Alert.
        """
        return dbc.Alert(
            message,
            id=id,
            color="primary",
            is_open=False,
            dismissable=True,
        )

    def get_success_message(
        self,
        message: str,
        id: str,
    ) -> dbc.Alert:
        """
        Get a preconfigured Alert success message.

        :param message: Message displayed in the alert.
        :param id: ID of the alert.
        :return: Alert.
        """
        return dbc.Alert(
            message,
            id=id,
            color="success",
            is_open=False,
            dismissable=True,
            duration=5000,
        )

    def _get_new_poi_modal_input_row(
        self,
        label: str,
        children: Any,
    ) -> dbc.Row:
        """
        Get a row with a label and children to be displayed in the "new POI" modal.

        :param label: Label to be displayed.
        :param children: Children to be displayed.
        :return: Row.
        """
        return dbc.Row(
            [dbc.Label(label, width=2), dbc.Col(children, width=10)],
            style={"margin-top": "0.5rem", "margin-bottom": "0.5rem"},
        )

    def get_new_poi_modal(self) -> dbc.Modal:
        """
        Get a modal to add a new POI.

        The modal contains the following fields:
        - Location: Display the coordinates of the clicked location.
        - Title: Input field for the title of the POI.
        - Category: Dropdown to select the category of the POI.
        - Date: Date picker to select the date of the POI.
        - Description: Input field for the description of the POI.

        Additionally, a header and footer with a button to create the POI is included.

        :return: Modal.
        """
        return dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("New POI"), close_button=True),
                dbc.ModalBody(
                    [
                        self._get_new_poi_modal_input_row(
                            "Location",
                            html.Span(id="add-poi-location", children="(NaN, NaN)"),
                        ),
                        self._get_new_poi_modal_input_row(
                            "Title",
                            dbc.Input(
                                id="add-poi-title",
                                type="text",
                                placeholder="Enter title ...",
                            ),
                        ),
                        self._get_new_poi_modal_input_row(
                            "Category",
                            dcc.Dropdown(
                                id="add-poi-category",
                                options=self.config.categories,
                                multi=True,
                                placeholder="Select categories ...",
                                className="dash-bootstrap",
                            ),
                        ),
                        self._get_new_poi_modal_input_row(
                            "Date",
                            dcc.DatePickerSingle(
                                id="add-poi-date",
                                initial_visible_month=date.today(),
                                date=date.today(),
                                first_day_of_week=2,
                            ),
                        ),
                        self._get_new_poi_modal_input_row(
                            "Description",
                            dbc.Input(
                                id="add-poi-description",
                                type="text",
                                placeholder="Enter description ...",
                            ),
                        ),
                    ]
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Create",
                        id="add-poi-modal-create",
                        className="ms-auto",
                        n_clicks=0,
                    )
                ),
            ],
            id="add-poi-modal",
            size="lg",
            centered=True,
            is_open=False,
        )

    def attach_new_poi_callbacks(self) -> None:
        """
        Attach callbacks that handle creating a new POI.
        """
        self._attach_show_toast_callback()
        self._attach_open_new_modal_callback()
        self._attach_create_poi_callback()
        self._attach_update_markers_callback()

    def _attach_show_toast_callback(self) -> None:
        """
        Attach a callback to show a toast message for the user to click on the map.
        """

        def show_toast(n_clicks: int) -> tuple[bool, bool, bool]:
            return True, True, True

        self.app.callback(
            Output("add-poi-toast", "is_open", allow_duplicate=True),
            Output("add-poi-modal-open", "disabled", allow_duplicate=True),
            Output("remove-poi-modal-open", "disabled", allow_duplicate=True),
            Input("add-poi-modal-open", "n_clicks"),
            prevent_initial_call=True,
        )(show_toast)

    def _attach_open_new_modal_callback(self) -> None:
        """
        Attach a callback to open the "new POI" modal.
        """

        def open_modal(coordinates: dict, is_open_modal: bool, is_open_toast: bool) -> tuple[str, bool, bool]:
            if coordinates and is_open_toast and not is_open_modal:
                lat, lng = coordinates["latlng"]["lat"], coordinates["latlng"]["lng"]
                self._log.debug(f"user clicked coordinates: {coordinates}")
                return f"({lat:.3f}, {lng:.3f})", True, False
            else:
                return "(NaN, NaN)", False, False

        self.app.callback(
            Output("add-poi-location", "children"),
            Output("add-poi-modal", "is_open", allow_duplicate=True),
            Output("add-poi-toast", "is_open"),
            Input("map", "clickData"),
            [State("add-poi-modal", "is_open"), State("add-poi-toast", "is_open")],
            prevent_initial_call=True,
        )(open_modal)

    def _validate_poi(self, poi: pd.DataFrame) -> pd.DataFrame:
        """
        Validate a POI.

        :param poi: POI to be validated.
        :return: Validated POI.
        """
        try:
            return POIData.validate(poi)
        except ValidationError as e:
            self._log.error(f"Validation error for new POI: {e}")
            self._log.error(poi)
            self._log.error(f"Traceback: {e}")

    def _attach_create_poi_callback(self) -> None:
        """
        Attach a callback to create a new POI.
        """

        def create_poi(
            n_clicks: int,
            coordinates: dict,
            title: str,
            category: str,
            date: str,
            description: str,
            is_open_toast: bool,
            is_open_success: bool,
        ) -> tuple[bool, bool, str, bool, bool, str | None, str | None, str, str | None, int]:
            if not is_open_toast:
                return (
                    False,
                    False,
                    "None",
                    False,
                    False,
                    None,
                    None,
                    date,
                    None,
                    0,
                )
            elif is_open_toast and n_clicks > 0 and coordinates:
                lat, lng = coordinates["latlng"]["lat"], coordinates["latlng"]["lng"]
                new_poi = pd.DataFrame(
                    {
                        "latitude": [lat],
                        "longitude": [lng],
                        "category": [np.array(category)],
                        "date": [datetime.strptime(date, "%Y-%m-%d").date()],
                        "title": [title],
                        "description": [description],
                    }
                )
                new_poi = self._validate_poi(new_poi)
                self.df = pd.concat([self.df, new_poi]).reset_index(drop=True)
                self._log.info("Added POI:")
                self._log.info(new_poi)

                self.df.to_parquet(self.config.database)
                self._log.info("Persisted database.")

                return (
                    False,
                    True,
                    f'Added POI "{title}"',
                    False,
                    False,
                    None,
                    None,
                    date,
                    None,
                    n_clicks,
                )
            else:
                return (
                    True,
                    False,
                    "None",
                    False,
                    False,
                    title,
                    category,
                    date,
                    description,
                    0,
                )

        self.app.callback(
            Output("add-poi-modal", "is_open", allow_duplicate=True),
            Output("new-poi-success", "is_open", allow_duplicate=True),
            Output("new-poi-success", "children"),
            Output("add-poi-modal-open", "disabled", allow_duplicate=True),
            Output("remove-poi-modal-open", "disabled", allow_duplicate=True),
            Output("add-poi-title", "value"),
            Output("add-poi-category", "value"),
            Output("add-poi-date", "date"),
            Output("add-poi-description", "value"),
            Output("add-poi-modal-create", "n_clicks"),
            [
                Input("add-poi-modal-create", "n_clicks"),
                Input("map", "clickData"),
                Input("add-poi-title", "value"),
                Input("add-poi-category", "value"),
                Input("add-poi-date", "date"),
                Input("add-poi-description", "value"),
            ],
            [
                State("add-poi-modal", "is_open"),
                State("new-poi-success", "is_open"),
            ],
            prevent_initial_call=True,
        )(create_poi)

    def get_remove_poi_modal(self) -> dbc.Modal:
        """
        Get a modal to remove a POI.

        :return: Modal.
        """
        return dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Remove POI"), close_button=True),
                dbc.ModalBody(
                    [
                        dcc.Dropdown(
                            id="remove-poi-dropdown",
                            options={},
                            multi=False,
                            placeholder="Select POI ...",
                            className="dash-bootstrap",
                        ),
                        html.Br(),
                        html.B("", id="remove-poi-title"),
                        html.Br(),
                        html.I("", id="remove-poi-category"),
                        html.Br(),
                        html.P("", id="remove-poi-description"),
                    ]
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Remove",
                        id="remove-poi-modal-remove",
                        className="ms-auto",
                        n_clicks=0,
                    )
                ),
            ],
            id="remove-poi-modal",
            size="lg",
            centered=True,
            is_open=False,
        )

    def attach_remove_poi_callbacks(self) -> None:
        """
        Attach callbacks that handle removing a POI.
        """
        self._attach_open_remove_modal_callback()
        self._attach_update_remove_poi_callback()
        self._attach_remove_poi_callback()

    def _attach_open_remove_modal_callback(self) -> None:
        """
        Attach a callback to open the "remove POI" modal.
        """

        def open_modal(n_clicks: int, is_open: bool) -> tuple[bool, dict]:
            dropdown_text_length = 80
            options = {}
            for i, row in self.df.iterrows():
                t = row.title
                d = row.description
                if len(d) > dropdown_text_length - len(t) - 6:
                    d = f"{d[:dropdown_text_length-len(t)-6]}..."
                options[i] = f"{t} ({d})"
            return True, options

        self.app.callback(
            Output("remove-poi-modal", "is_open"),
            Output("remove-poi-dropdown", "options"),
            Input("remove-poi-modal-open", "n_clicks"),
            [State("add-poi-modal", "is_open")],
            prevent_initial_call=True,
        )(open_modal)

    def _attach_update_remove_poi_callback(self) -> None:
        """
        Attach a callback to update the "remove POI" modal contents.
        """

        def update_remove_modal(value: str) -> tuple[str, str, str]:
            if value:
                selected = self.df.iloc[int(value)]
                title = selected.title
                category = f"{', '.join(selected.category)}"
                description = selected.description
                return title, category, description
            else:
                return "Select a POI to remove.", "", ""

        self.app.callback(
            Output("remove-poi-title", "children"),
            Output("remove-poi-category", "children"),
            Output("remove-poi-description", "children"),
            Input("remove-poi-dropdown", "value"),
            prevent_initial_call=True,
        )(update_remove_modal)

    def _attach_remove_poi_callback(self) -> None:
        """
        Attach a callback to remove a POI.
        """

        def remove_poi(
            value: str,
            n_clicks: int,
            is_open_modal: bool,
            is_open_success: bool,
        ) -> tuple[bool, int, bool, str | None, str | None]:
            if not is_open_modal:
                return False, 0, False, None, None
            elif value is not None and is_open_modal and n_clicks > 0:
                selected = self.df.iloc[int(value)]
                self.df = self.df.drop(int(value)).reset_index(drop=True)
                self._log.info("Removed POI:")
                self._log.info(selected)

                self.df.to_parquet(self.config.database)
                self._log.info("Persisted database.")

                return (False, 0, True, f'Removed POI "{selected.title}"', None)
            else:
                return True, 0, False, None, value

        self.app.callback(
            Output("remove-poi-modal", "is_open", allow_duplicate=True),
            Output("remove-poi-modal-remove", "n_clicks"),
            Output("remove-poi-success", "is_open", allow_duplicate=True),
            Output("remove-poi-success", "children"),
            Output("remove-poi-dropdown", "value"),
            [
                Input("remove-poi-dropdown", "value"),
                Input("remove-poi-modal-remove", "n_clicks"),
            ],
            [
                State("remove-poi-modal", "is_open"),
                State("remove-poi-success", "is_open"),
            ],
            prevent_initial_call=True,
        )(remove_poi)

    def _attach_update_markers_callback(self) -> None:
        """
        Attach a callback to update the markers on the map.
        """

        def update_markers(df: pd.DataFrame) -> dl.FeatureGroup:
            """
            Generate updated markers based on the current DataFrame.

            :param df: The updated DataFrame.
            :return: A list of updated map components.
            """
            self._log.debug(f"Updating markers with {len(df)} entries.")
            return dl.FeatureGroup([self.format_marker(marker) for marker in self.get_markers(df)])

        self.app.callback(
            Output("map-markers", "children"),
            [
                Input("add-poi-modal-create", "n_clicks"),
                Input("remove-poi-modal-remove", "n_clicks"),
            ],
            prevent_initial_call=True,
        )(lambda _create_clicks, _remove_clicks: update_markers(self.df))

    def format_marker(self, marker: dict) -> dl.Marker:
        return dl.Marker(
            position=marker["position"],
            children=[
                dl.Tooltip(
                    children=[
                        html.Div(
                            [
                                html.B(marker["title"]),
                                html.Br(),
                                html.Span(marker["date"]),
                                html.Br(),
                                html.I(", ".join(marker["category"])),
                                html.Br(),
                                html.Span(marker["description"]),
                            ],
                            className="marker-tooltip",
                        )
                    ]
                )
            ],
        )

    def build(self) -> None:
        """
        Build the app:
        - Build the sidebar.
        - Build the main part.
        """
        self.build_sidebar()
        self.build_main()
        self.app.layout = html.Div([self.sidebar, self.content])

    def run(self) -> None:
        """
        Run the app.

        Before the app can run, it must be built using the `build` method.
        """
        self.app.run(
            host="0.0.0.0",
            port=str(self.config.port),
            debug=self.config.loglevel == "DEBUG",
        )
