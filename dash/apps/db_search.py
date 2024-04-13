from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import requests

from utils.colors import custom_colors
from app import app


# Define sorting options
sort_options = dbc.RadioItems(
    options=[
        {"label": "New to Old", "value": "new_to_old"},
        {"label": "Old to New", "value": "old_to_new"},
        {"label": "Score", "value": "score"},
    ],
    value="new_to_old",  # Default value
    id="sort-options",
    inline=True,
    style={"color": custom_colors["dark-blue"]},
)

# Define the layout for the database search page
layout = dbc.Container(
    [
        html.H2("Database Search", style={"color": custom_colors["dark-blue"]}),
        dbc.Input(
            id="db-search-input",
            placeholder="Enter search term",
            type="text",
            style={"color": custom_colors["dark-blue"]},
        ),
        sort_options,
        dbc.Button(
            "Search",
            id="db-search-btn",
            color="primary",
            className="mt-2",
            style={"background-color": custom_colors["teal"]},
        ),
        html.Div(
            id="db-search-results",
            style={"color": custom_colors["dark-blue"]},
        ),
    ]
)


@app.callback(
    Output("db-search-results", "children"),
    [Input("db-search-btn", "n_clicks")],
    [State("db-search-input", "value"), State("sort-options", "value")],
)
def update_db_search_results(n_clicks, search_term, sort_order):
    """
    This function updates the database search results based on the search term and sort order.

    Parameters:
    ----------
    n_clicks (int): The number of times the search button has been clicked.
    search_term (str): The search term entered by the user.
    sort_order (str): The sorting order selected by the user.

    Returns:
    --------
    html.Div: The search results displayed as a table.

    Raises:
    -------
    PreventUpdate: If no input is provided.
    """
    if n_clicks is None or search_term is None:
        # Prevents the callback from being triggered without input
        raise PreventUpdate

    response = requests.get(
        f"http://127.0.0.1:8000/search/?term={search_term}&sort={sort_order}"
    )
    if response.status_code == 200:
        articles = response.json()
        if articles:
            # If articles are found, display them
            table_header = [
                html.Th("Title", style={"color": custom_colors["dark-blue"]}),
                html.Th("DOI", style={"color": custom_colors["dark-blue"]}),
                html.Th(
                    "Date", style={"color": custom_colors["dark-blue"], "width": "10%"}
                ),
                html.Th(
                    "Score",
                    style={"color": custom_colors["dark-blue"], "width": "4.5%"},
                ),
            ]
            table_rows = [
                html.Tr(
                    [
                        html.Td(article["title"]),
                        html.Td(article["doi"]),
                        html.Td(article["date"]),
                        html.Td(article["score"]),
                    ]
                )
                for article in articles
            ]
            return dbc.Table(
                [html.Thead(table_header), html.Tbody(table_rows)],
                bordered=True,
                hover=True,
                responsive=True,
                striped=True,
            )
        else:
            # If no articles are found, display a message including the search term
            return html.P(
                f"No articles found matching the search term: '{search_term}'.",
                style={"color": custom_colors["dark-blue"]},
            )
    else:
        # If there's an error with the request, display a generic error message
        return html.P(
            "An error occurred while fetching search results.",
            style={"color": custom_colors["dark-blue"]},
        )
