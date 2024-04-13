from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from app import app
from apps import home, about, db_search, navigation, search

url_content_layout = dbc.Container(
    [
        dcc.Location(id="url", refresh=False),
        navigation.layout,
        dbc.Container(id="page-content", className="mt-4"),
    ]
)

app.layout = url_content_layout

app.validation_layout = html.Div(
    [
        url_content_layout,
        home.layout,
        about.layout,
        db_search.layout,
        search.layout,
        navigation.layout,
    ]
)


# Update the page content based on the URL
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")],
)
def display_page(pathname):
    if pathname == "/":
        return home.layout
    elif pathname == "/about":
        return about.layout
    elif pathname == "/search":
        return search.layout
    elif pathname == "/dbsearch":
        return db_search.layout
    else:
        return home.layout


# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)
