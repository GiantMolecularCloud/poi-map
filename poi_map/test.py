import dash
from dash import Output, Input, State, html, callback
import dash_leaflet as dl


app = dash.Dash(__name__)
app.layout = html.Div(
    [
        dl.Map(center=[56, 10], zoom=4, children=[
            dl.TileLayer(), dl.FeatureGroup([
                dl.EditControl(
                    id="edit_control",
                    draw=dict(
                        circlemarker=False,
                    ),
                ),
                dl.Marker(position=[56, 10])]),
        ], style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "inline-block"},
               id="map"
        ),
        html.Button(children="Toggle edit mode", id="btn", n_clicks=0),
    ]
)

@callback(
    Output("edit_control", "draw"),
    Input("btn", "n_clicks"),
    State("edit_control", "draw"),
    prevent_initial_call=True
)
def sdf(n_clicks, draw):
    if n_clicks > 0:
        return dict(
            circlemarker=True,
            line=False,
            polygon=False,
            rectangle=False,
            circle=False,
            marker=False,
            polyline=False,
        )

if __name__ == '__main__':
    app.run_server(port=8850, debug=False)