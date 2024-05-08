from dash import html, ctx, no_update
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_ag_grid as ag
from dash.exceptions import PreventUpdate
import requests

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

# Popup displaying article information
article_popup = dbc.Modal(
    [
        dbc.ModalHeader(
            "Article", style={"color": custom_colors["dark-blue"]}
        ),
        dbc.ModalBody(id="article-body-modal"),
        dbc.ModalFooter(
            dbc.Button(
                "Close",
                id="article-modal-close",
                className="ml-auto",
                style={"background-color": custom_colors["teal"]},
            )
        ),
    ],
    id="article-selection-modal",
    size="xl",
    is_open=False,
    scrollable=True,
)

# Layout for the database search page
layout = dbc.Container(
    [
        html.H2("Database Search", style={"color": custom_colors["dark-blue"]}),
        # Input field and search button
        dbc.InputGroup(
            [
                dbc.Input(
                    id="db-search-input",
                    placeholder="Enter search term",
                    type="text",
                    style={"color": custom_colors["dark-blue"]},
                ),
                dbc.Button(
                    "Search",
                    id="db-search-btn",
                    color="primary",
                    n_clicks=0,
                    style={"background-color": custom_colors["teal"]},
                ),
            ]
        ),
        sort_options,
        # Display search results
        html.Div(
            [
                html.Div(
                    id="db-search-results",
                    style={"color": custom_colors["dark-blue"]},
                ),
            ],
            style={"margin-top": "20px"},  # Add margin top
        ),
        # Display article information modal when a row is selected
        article_popup,
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
            # Define the columns for the search results table
            columnDefs = [
                {"field": "title", "width": 700, "suppressSizeToFit": True},
                {"field": "doi", "headerName": "DOI", "width": 300},
                {"field": "date"},
                {"field": "score"},
            ]

            # Create a list of dictionaries for the search results
            article_data = [
                {
                    "id": i,
                    "title": article["title"],
                    "doi": article["doi"],
                    "date": article["date"],
                    "score": article["score"],
                }
                for i, article in enumerate(articles)
            ]

            # Create an Ag-Grid table with the search results
            grid = ag.AgGrid(
                id="db-results-grid",
                rowData=article_data,
                columnDefs=columnDefs,
                dashGridOptions={
                    "rowSelection": "single",
                    "pagination": True,
                    "groupHeaderHeight": 100,
                    "enableCellTextSelection": True,
                    "ensureDomOrder": True,
                    "defaultColDef": {
                        "filter": True,
                        "filterParams": {
                            "buttons": ["apply", "reset"],
                            "closeOnApply": True,
                            "suppressAndOrCondition": True,
                            "inRangeInclusive": True,
                        },
                    },
                },
                columnSize="sizeToFit",
                style={"height": 800, "width": "100%"},
                className="ag-theme-quartz",
            )

            return grid

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
    Output("article-selection-modal", "is_open"),
    Output("article-body-modal", "children"),
    Input("db-results-grid", "selectedRows"),
    Input("article-modal-close", "n_clicks"),
    prevent_initial_call=True,
)
def display_article_modal(selection, _):
    """
    This function displays the article information modal when a row is selected in the search results.

    Parameters:
    ----------
    selection (list): The selected row in the search results.
    _ (int): The number of times the close button has been clicked.

    Returns:
    --------
    bool: Whether the modal is open or closed.
    html.Div: The article information displayed in the modal.

    Raises:
    -------
    PreventUpdate: If no input is provided.
    """
    if not ctx.triggered or ctx.triggered_id == "article-modal-close":
        return False, no_update

    if not selection:
        return no_update, no_update

    article_doi = selection[0].get("doi")
    if not article_doi:
        return no_update, no_update

    article_info = get_article_info(article_doi)
    if article_info is None:
        return False, no_update
    return True, article_info
