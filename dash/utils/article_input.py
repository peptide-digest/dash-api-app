import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import requests

from app import app
from utils.colors import custom_colors

# Create a dropdown menu for the article type
articletype_menu = [
    dbc.DropdownMenuItem("DOI", id="doi-dropdown"),
    dbc.DropdownMenuItem("URL", id="url-dropdown"),
    dbc.DropdownMenuItem("PII", id="pii-dropdown"),
]


# Create an input field for the article
article_id_input = dbc.InputGroup(
    [
        dbc.DropdownMenu(
            articletype_menu,
            label="Select Type",
            id="articletype-dropdown",
            color=custom_colors["teal"],
        ),
        dbc.Input(
            id="user-input-article-type",
            type="text",
            placeholder="Enter article DOI/URL/PII",
            style={"color": custom_colors["dark-blue"]},
        ),
        dbc.Button(
            "Submit",
            id="submit-btn",
            color="primary",
            n_clicks=0,
            style={"background-color": custom_colors["teal"]},
        ),
    ],
    className="mb-3",
)


# Define callback to update the article type label
@app.callback(
    Output("articletype-dropdown", "label"),
    [
        Input("doi-dropdown", "n_clicks"),
        Input("url-dropdown", "n_clicks"),
        Input("pii-dropdown", "n_clicks"),
    ],
)
def update_label(n1, n2, n3):
    """
    This function returns the label for the article type dropdown menu.

    Parameters:
        n1 (int): The number of clicks for the DOI dropdown menu.
        n2 (int): The number of clicks for the URL dropdown menu.
        n3 (int): The number of clicks for the PII dropdown menu.

    Returns:
        str: The label for the article type dropdown menu.
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = "doi-dropdown"  # default value
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "doi-dropdown":
        return "DOI"
    elif button_id == "url-dropdown":
        return "URL"
    elif button_id == "pii-dropdown":
        return "PII"
    else:
        return "DOI"  # Default value


@app.callback(
    Output("user-input-article-type", "placeholder"),
    [
        Input("doi-dropdown", "n_clicks"),
        Input("url-dropdown", "n_clicks"),
        Input("pii-dropdown", "n_clicks"),
    ],
)
def update_placeholder(n1, n2, n3):
    """
    This function returns the placeholder for the article type input field.

    Parameters:
        n1 (int): The number of clicks for the DOI dropdown menu.
        n2 (int): The number of clicks for the URL dropdown menu.
        n3 (int): The number of clicks for the PII dropdown menu.

    Returns:
        str: The placeholder for the article type input field.
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = "doi-dropdown"  # default value
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "doi-dropdown":
        return "Enter article DOI"
    elif button_id == "url-dropdown":
        return "Enter article URL"
    elif button_id == "pii-dropdown":
        return "Enter article PII"
    else:
        return "Enter article DOI"


@app.callback(
    Output("article-info", "children"),
    [Input("submit-btn", "n_clicks")],
    [State("user-input-article-type", "value"), State("articletype-dropdown", "label")],
)
def update_article_info(n_clicks, input_value, article_type):
    """
    This function updates the article information based on the user input.

    Parameters:
    ----------
    n_clicks (int): The number of times the submit button has been clicked.
    input_value (str): The article identifier entered by the user.
    article_type (str): The type of article identifier (DOI, URL, or PII).

    Returns:
    -------
    html.Div: A Div containing the detailed information about the article.

    Raises:
    -------
    PreventUpdate: If no input is provided.
    """
    if n_clicks is None or n_clicks < 1:
        raise PreventUpdate

    query_param = (
        "doi" if article_type == "DOI" else "url" if article_type == "URL" else "pii"
    )
    response = requests.get(
        f"http://127.0.0.1:8000/retrieve/?{query_param}={input_value}"
    )

    if response.status_code == 200:
        article_info = response.json()

        detailed_info = html.Div(
            [
                html.H5(
                    "Article Information:", style={"color": custom_colors["dark-blue"]}
                ),
                html.P(
                    html.A(
                        article_info["title"],
                        href=article_info["url"],
                        target="_blank",  # Open link in a new tab
                        style={"color": custom_colors["dark-blue"]},
                    )
                ),
            ],
            className="article-detailed-info",
        )

        # Tabbed interface
        tabbed_interface = dbc.Tabs(
            [
                dbc.Tab(
                    dcc.Markdown(
                        f"**Bullet Points:**\n{article_info['model_bullet_points']}\n\n"
                        f"**Summary:**\n{article_info['model_summary']}"
                    ),
                    label="Summary",
                ),
                dbc.Tab(
                    dcc.Markdown(
                        f"**Score:**\n{article_info['model_score']}\n\n"
                        f"**Scoring Reasoning:**\n{article_info['model_score_justification']}"
                    ),
                    label="Scoring Criteria",
                ),
                dbc.Tab(
                    dcc.Markdown(f"**Metadata:**\n{article_info['model_metadata']}"),
                    label="Metadata",
                ),
            ],
            className="article-tabs",
        )

        # Combine detailed info and tabs in a single Div to avoid list of lists
        return html.Div([detailed_info, tabbed_interface])
    else:
        return html.P(
            "Article not found or error in fetching information.",
            style={"color": custom_colors["dark-blue"]},
        )
