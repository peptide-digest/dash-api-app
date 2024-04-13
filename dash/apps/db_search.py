from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
import requests
import dash
import json

from utils.colors import custom_colors
from utils.article_input import get_article_info
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


modal_trigger = html.Button(
    "Open Modal", id="open-modal-btn", style={"display": "none"}
)  # Add a button to trigger the modal
modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(
                    "Article Information", style={"color": custom_colors["dark-blue"]}
                ),
                dbc.ModalBody(id="modal-article-body"),
            ],
            id="modal-article",
            size="xl",
            is_open=False,
        )
    ]
)


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
        modal_trigger,
        modal,
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
                    ],
                    id={"type": "table-row", "index": i},  # Add an id to each table row
                    n_clicks=0,
                    style={"cursor": "pointer"},
                )
                for i, article in enumerate(articles)
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


@app.callback(
    Output("modal-article", "is_open"),
    Output("modal-article-body", "children"),
    [Input({"type": "table-row", "index": ALL}, "n_clicks")],
    [
        State("modal-article", "is_open"),
        State({"type": "table-row", "index": ALL}, "id"),
        State({"type": "table-row", "index": ALL}, "children"),
    ],  # Capture all row children
)
def toggle_modal_from_table_row_click(n_clicks_list, is_open, row_ids, row_children):
    ctx = dash.callback_context
    if not ctx.triggered:
        return is_open, None

    clicked_row_id = ctx.triggered[0]["prop_id"].split(".")[0]
    clicked_row_id_dict = json.loads(clicked_row_id)
    row_idx = clicked_row_id_dict["index"]

    if any(n_clicks_list):
        clicked_row_children = row_children[row_idx]
        doi = clicked_row_children[1]["props"]["children"]
        return True, get_article_info(doi)

    return is_open, None
