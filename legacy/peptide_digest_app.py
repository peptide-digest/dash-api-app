import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import requests
import json

# Custom colors for the app
custom_colors = {"teal": "#00857C", "dark-blue": "#0C2340"}

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

# Pop-up modal for displaying detailed article information
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


# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
    suppress_callback_exceptions=True,
)

server = app.server

navigation_layout = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Img(src=dash.get_asset_url("logo.png"), width="40"),
                            dbc.NavbarBrand("Peptide Digest", className="ms-2"),
                        ],
                        width={"size": "auto"},
                    )
                ],
                align="center",
                className="g-0",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Nav(
                                [
                                    dbc.NavItem(dbc.NavLink("Home", href="/")),
                                    dbc.NavItem(
                                        dbc.NavLink(
                                            html.I(className="bi bi-search"),
                                            href="/search",
                                        )
                                    ),
                                    dbc.NavItem(
                                        dbc.NavLink("DB Search", href="/dbsearch")
                                    ),
                                    dbc.NavItem(dbc.NavLink("About", href="/about")),
                                    dbc.NavItem(
                                        dbc.NavLink(
                                            html.I(className="bi bi-github"),
                                            href="https://github.com/peptide-digest",
                                            target="_blank",
                                            external_link=True,
                                        )
                                    ),
                                ],
                                navbar=True,
                            )
                        ],
                        width={"size": "auto"},
                    )
                ],
                align="center",
            ),
        ],
        fluid=True,
    ),
    color=custom_colors["teal"],
    dark=True,
)

# Define the layout of the application
app.layout = dbc.Container(
    [
        navigation_layout,
        # Page content will be rendered by the callback
        dcc.Location(id="url", refresh=False),
        dbc.Container(id="page-content", className="mt-4"),
    ]
)


# Define callback to update page content based on URL
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/search":
        # Content for the 'Search' page
        return dbc.Container(
            [
                html.H2(
                    "Search for Articles", style={"color": custom_colors["dark-blue"]}
                ),
                article_id_input,  # Include the updated input group here
                html.Div(
                    id="article-info",
                    style={"color": custom_colors["dark-blue"]},
                ),
            ]
        )
    elif pathname == "/about":
        # Content for the 'About' page
        return dbc.Container(
            [
                html.H2(
                    "Welcome to Peptide Digest!",
                    style={"color": custom_colors["dark-blue"]},
                ),
                html.Br(),
                html.P(
                    "We are a team of UC Berkeley students in the Master of Molecular Science and Software Engineering (MSSE) program working with Merck to develop a tool that provides efficient summaries of scientific publications! Our goal is to help Merck researchers stay updated with the latest computational peptide research.",
                    style={"color": custom_colors["dark-blue"]},
                ),
                html.P(
                    "Our team members include: Joshua Blomgren, Elizabeth Gilson, and Jeffrey Jacob.",
                    style={"color": custom_colors["dark-blue"]},
                ),
                html.P(
                    "We are advised by Dr. Jennifer Johnston, Dr. Gregory Bryman, Dr. Tianchi Chen, and Dr. Wendong Ge from Merck and by Dr. Jessica Nash from MSSE.",
                    style={"color": custom_colors["dark-blue"]},
                ),
            ]
        )

    elif pathname == "/dbsearch":
        return dbc.Container(
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

    else:
        # Default content, assuming the homepage or an undefined path
        return dbc.Container(
            [
                html.H1(
                    "Peptide Digest",
                    style={"textAlign": "center", "color": custom_colors["dark-blue"]},
                ),
                html.P(
                    "This tool provides efficient summaries of scientific publications, helping researchers stay updated with the latest computational peptide research.",
                    style={"color": custom_colors["dark-blue"]},
                ),
                html.P(
                    "Get started by selecting an article type and entering a DOI, URL, or PII below.",
                    style={"color": custom_colors["dark-blue"]},
                ),
                html.Hr(),
                article_id_input,  # The input section with the submit button
                html.Div(
                    id="article-info",
                    style={"color": custom_colors["dark-blue"]},
                ),  # This will display the results
            ],
            className="mt-4",
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

        feedback_tab = dbc.Tab(
            [
                dbc.Input(id="name-input", placeholder="Enter your name", type="text"),
                dbc.Input(id="doi-input", placeholder="Enter the article DOI", type="text"),
                dbc.Textarea(id="feedback-input", placeholder="Enter your feedback", rows=3),
                dbc.Button("Submit Feedback", id="submit-feedback-btn", color="primary", className="mt-2"),
                html.Div(id="feedback-message")
            ],
            label="Submit Feedback"
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
                    # Add a callback to toggle the modal when the table row is clicked
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
    ],
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
        article_info = get_article_info(doi)
        if article_info is None:
            return is_open, None
        return True, article_info

    return is_open, None


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

        feedback_tab = dbc.Tab(
        [
            dbc.Input(id="name-input", placeholder="Enter your name", type="text"),
            dbc.Input(id="doi-input", placeholder="Enter the article DOI", type="text"),
            dbc.Textarea(id="feedback-input", placeholder="Enter your feedback", rows=3),
            dbc.Button("Submit Feedback", id="submit-feedback-btn", color="primary", className="mt-2"),
            html.Div(id="feedback-message")
        ],
        label="Submit Feedback"
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

                feedback_tab
            ],
            className="article-tabs",
        )

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
        with open("../data/feedback.csv", "a") as f:
            f.write(f"{name},{feedback},{doi}\n")
        return "Feedback submitted successfully!"
    else:
        return "Please enter your name, the article DOI, and feedback."


# Run the application
if __name__ == "__main__":
    app.run_server(debug=True)
