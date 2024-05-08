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
                html.H5("Article Information:", style={"color": custom_colors["dark-blue"]}),
                html.P(f"DOI: {article_info['doi']}", id="displayed-doi", style={"color": custom_colors["dark-blue"]}),

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


        feedback_tab = dbc.Tab(
            [
                dbc.Input(id="name-input", placeholder="Enter your name", type="text"),
                dbc.Input(id="doi-input", value="", placeholder="Enter the article DOI", type="text"),
                dbc.Textarea(id="feedback-input", placeholder="Enter your feedback", rows=3),
                dbc.Button("Submit Feedback", id="submit-feedback-btn", color="success", className="mt-2"),
                html.Div(id="feedback-message")
            ],
            label="Submit Feedback"
        )

        # Tabbed interface
        tabbed_interface = dbc.Tabs(
            [
                dbc.Tab(
                    dcc.Markdown(
                        f"**Authors:**\n{article_info['authors']}\n\n"
                        f"**Journal:**\n{article_info['journal']}\n\n"
                        f"**Date:**\n{article_info['date']}\n\n"
                        f"**DOI:**\n{article_info['doi']}\n\n"
                        f"**Keywords:**\n{article_info['keywords']}"
                    ),
                    label="Article Info",
                ),
                dbc.Tab(
                    dcc.Markdown(
                        f"**Bullet Points:**\n{article_info['bullet_points']}\n\n"
                        f"**Summary:**\n{article_info['summary']}"
                    ),
                    label="Summary",
                ),
                dbc.Tab(
                    dcc.Markdown(
                        f"**Score:**\n{article_info['score']}\n\n"
                        f"**Scoring Reasoning:**\n{article_info['score_justification']}"
                    ),
                    label="Scoring Criteria",
                ),
                dbc.Tab(
                    dcc.Markdown(f"**Metadata:**\n{article_info['metadata']}"),
                    label="Metadata",
                ),

                feedback_tab
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


def get_article_info(input_doi):
    """
    This function retrieves the article information based on the DOI.

    Parameters:
    ----------
    input_doi (str): The DOI of the article.

    Returns:
    -------
    html.Div: A Div containing the detailed information about the article.
    """
    response = requests.get(f"http://127.0.0.1:8000/retrieve/?doi={input_doi}")

    if response.status_code == 200:
        article_info = response.json()

        detailed_info = html.Div(
            [
                html.H5("Article Information:", style={"color": custom_colors["dark-blue"]}),
                html.H5(f"DOI: {article_info['doi']}", id="displayed-doi", style={"color": custom_colors["dark-blue"]}),

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

        feedback_tab = dbc.Tab(
            [
                dbc.Input(id="name-input", placeholder="Enter your name", type="text"),
                dbc.Input(id="doi-input", value="", placeholder="Enter the article DOI", type="text"),
                dbc.Textarea(id="feedback-input", placeholder="Enter your feedback", rows=3),
                dbc.Button("Submit Feedback", id="submit-feedback-btn", color="success", className="mt-2"),
                html.Div(id="feedback-message")
            ],
            label="Submit Feedback"
        )
        # Tabbed interface
        tabbed_interface = dbc.Tabs(
            [
                dbc.Tab(
                    dcc.Markdown(
                        f"**Authors:**\n{article_info['authors']}\n\n"
                        f"**Journal:**\n{article_info['journal']}\n\n"
                        f"**Date:**\n{article_info['date']}\n\n"
                        f"**DOI:**\n{article_info['doi']}\n\n"
                        f"**Keywords:**\n{article_info['keywords']}"
                    ),
                    label="Article Info",
                ),
                dbc.Tab(
                    dcc.Markdown(
                        f"**Bullet Points:**\n{article_info['bullet_points']}\n\n"
                        f"**Summary:**\n{article_info['summary']}"
                    ),
                    label="Summary",
                ),
                dbc.Tab(
                    dcc.Markdown(
                        f"**Score:**\n{article_info['score']}\n\n"
                        f"**Scoring Reasoning:**\n{article_info['score_justification']}"
                    ),
                    label="Scoring Criteria",
                ),
                dbc.Tab(
                    dcc.Markdown(f"**Metadata:**\n\n{article_info['metadata']}"),
                    label="Metadata",
                ),
                feedback_tab
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


@app.callback(
    Output("feedback-message", "children"),
    [Input("submit-feedback-btn", "n_clicks")],
    [State("name-input", "value"), State("doi-input", "value"), State("feedback-input", "value")]
)
def submit_feedback(n_clicks, name, doi, feedback):
    if n_clicks is None:
        raise PreventUpdate

    if name and doi and feedback:
        try:
            with open("/usr/src/app/data/feedback.csv", "a") as f:
                f.write(f"{name},{feedback},{doi}\n")
                f.flush()  # Flush the file buffer
                print("Feedback data written to file")  # Print a message to indicate success
            return "Feedback submitted successfully!"
        except Exception as e:
            print(f"Error writing feedback data to file: {str(e)}")  # Print any error that occurs
            return "An error occurred while submitting the feedback."
    else:
        return "Please enter your name, the article DOI, and feedback."
        
@app.callback(
    Output("doi-input", "value"),
    [Input("displayed-doi", "children")]
)
def update_doi_input(displayed_doi):
    if displayed_doi:
        doi = displayed_doi.split(': ')[1]
        return doi
    else:
        return ""