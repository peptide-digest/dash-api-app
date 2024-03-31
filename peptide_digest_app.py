import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc  
from dash.exceptions import PreventUpdate
import requests

# Define sorting options
sort_options = dbc.RadioItems(
    options=[
        {"label": "New to Old", "value": "new_to_old"},
        {"label": "Old to New", "value": "old_to_new"}
    ],
    value="new_to_old",  # Default value
    id="sort-options",
    inline=True
)

# Create a dropdown menu for the article type
articletype_menu = [
    dbc.DropdownMenuItem("DOI", id='doi-dropdown'),
    dbc.DropdownMenuItem("URL", id='url-dropdown'),
    dbc.DropdownMenuItem("PII", id='pii-dropdown'),
]

# Create an input field for the article
article_id_input = dbc.InputGroup([
    dbc.DropdownMenu(articletype_menu, label="Select Type", id='articletype-dropdown'),
    dbc.Input(id='user-input-article-type', type='text', placeholder="Enter article DOI/URL/PII"),
    dbc.Button("Submit", id="submit-btn", color="primary", n_clicks=0),
], className="mb-3")


# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}],
                suppress_callback_exceptions=True)

# Define the layout of the application
app.layout = dbc.Container([
    # Navbar
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="/")),
            dbc.NavItem(dbc.NavLink("Search", href="/search")),
            dbc.NavItem(dbc.NavLink("DB Search", href="/dbsearch")),  # Add DB Search link
            dbc.NavItem(dbc.NavLink("About", href="/about")),
        ],
        brand="Peptide Digest",
        brand_href="/",
        color="primary", 
        dark=True,
    ),
    
    # Page content will be rendered by the callback
    dcc.Location(id='url', refresh=False),
    dbc.Container(id='page-content', className='mt-4')  # Use dbc.Container for content area
])

# Define callback to update page content based on URL
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/search':
        # This part is specifically for the search page
        return dbc.Container([
            html.H2("Search for Articles"),
            article_id_input,  # Include the updated input group here
            html.Div(id="article-info"),  # Area to display the fetched article information
        ])
    elif pathname == '/about':
        # Content for the 'About' page
        return dbc.Container([
            html.H2("Welcome to Peptide Digest!"),
            html.Br(),
            html.P("We are a team of UC Berkeley students in the Master of Molecular Science and Software Engineering (MSSE) program working with Merck to develop a tool that provides efficient summaries of scientific publications! Our goal is to help Merck researchers stay updated with the latest computational peptide research."),
            html.P("Our team members include: Joshua Blomgren, Elizabeth Gilson, and Jeffrey Jacob."),
            html.P("We are advised by Dr. Jennifer Johnston, Dr. Gregory Bryman, Dr. Tianchi Chen, and Dr. Wendong Ge from Merck and by Dr. Jessica Nash from MSSE."),
        ])
    
    elif pathname == '/dbsearch':
        return dbc.Container([
            html.H2("Database Search"),
            dbc.Input(id="db-search-input", placeholder="Enter search term", type="text"),
            sort_options,  # Include sorting options here
            dbc.Button("Search", id="db-search-btn", color="primary", className="ms-2"),
            html.Div(id="db-search-results"),
        ])
    
    else:
        # Default content, assuming the homepage or an undefined path
        return dbc.Container([
            html.H1("Peptide Digest", style={'textAlign': 'center'}),
            html.P("This tool provides efficient summaries of scientific publications, helping researchers stay updated with the latest computational peptide research."),
            html.P("Get started by selecting an article type and entering a DOI, URL, or PII below."),
            html.Hr(),
            article_id_input,  # The updated input section with the submit button
            html.Div(id="article-info"),  # This will display the results
        ], className="mt-4")


# Define callback to update the article type label
@app.callback(
    Output('articletype-dropdown', 'label'),
    [
        Input('doi-dropdown', 'n_clicks'),
        Input('url-dropdown', 'n_clicks'),
        Input('pii-dropdown', 'n_clicks'),
    ],
)
def update_label(n1, n2, n3):
    '''
    This function returns the label for the article type dropdown menu.
    
    Parameters:
        n1 (int): The number of clicks for the DOI dropdown menu.
        n2 (int): The number of clicks for the URL dropdown menu.
        n3 (int): The number of clicks for the PII dropdown menu.
        
    Returns:
        str: The label for the article type dropdown menu.
    '''
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'doi-dropdown'  # default value
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'doi-dropdown':
        return "DOI"
    elif button_id == 'url-dropdown':
        return "URL"
    elif button_id == 'pii-dropdown':
        return "PII"
    else:
        return "DOI"  # Default value
    
@app.callback(
    Output('user-input-article-type', 'placeholder'),
    [
        Input('doi-dropdown', 'n_clicks'),
        Input('url-dropdown', 'n_clicks'),
        Input('pii-dropdown', 'n_clicks'),
    ],
)
def update_placeholder(n1, n2, n3):
    '''
    This function returns the placeholder for the article type input field.

    Parameters:
        n1 (int): The number of clicks for the DOI dropdown menu.
        n2 (int): The number of clicks for the URL dropdown menu.
        n3 (int): The number of clicks for the PII dropdown menu.

    Returns:
        str: The placeholder for the article type input field.
    '''
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'doi-dropdown'  # default value
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'doi-dropdown':
        return "Enter article DOI"
    elif button_id == 'url-dropdown':
        return "Enter article URL"
    elif button_id == 'pii-dropdown':
        return "Enter article PII"
    else:
        return "Enter article DOI"



# Callback for submitting DOI/URL and updating the article information
@app.callback(
    Output("article-info", "children"),
    [Input("submit-btn", "n_clicks")],
    [State("user-input-article-type", "value"),
     State("articletype-dropdown", "label")],
)
def update_article_info(n_clicks, input_value, article_type):
    if n_clicks is None or n_clicks < 1:
        # No clicks yet, or the button hasn't been clicked.
        raise PreventUpdate
    
    # Construct the query URL based on the selected article type and input value
    query_param = 'doi' if article_type == 'DOI' else 'url'
    response = requests.get(f"http://127.0.0.1:8000/retrieve/?{query_param}={input_value}")

    if response.status_code == 200:
        article_info = response.json()
        # Use dcc.Markdown to format and return the desired information from the article, respecting newline characters
        return [
            html.H5("Article Information:"),
            html.P(f"Title: {article_info['title']}"),
            dcc.Markdown(f"**Bullet Points:**\n{article_info['model_bullet_points']}"),
            dcc.Markdown(f"**Metadata:**\n{article_info['model_metadata']}"),
            dcc.Markdown(f"**Summary:**\n{article_info['model_summary']}"),
            # Include more fields as necessary
        ]
    else:
        # Handle errors or article not found
        return html.P("Article not found or error in fetching information.")


@app.callback(
    Output("db-search-results", "children"),
    [Input("db-search-btn", "n_clicks")],
    [State("db-search-input", "value"), State("sort-options", "value")],
)
def update_db_search_results(n_clicks, search_term, sort_order):
    if n_clicks is None or search_term is None:
        # Prevents the callback from being triggered without input
        raise PreventUpdate

    response = requests.get(f"http://127.0.0.1:8000/search/?term={search_term}&sort={sort_order}")
    if response.status_code == 200:
        articles = response.json()
        if articles:
            # If articles are found, display them
            return [html.Div([
                html.H3(article['title']),
                html.P(f"DOI: {article['doi']}"),
                html.P(f"Date: {article['date']}")
            ], style={'margin-bottom': '20px'}) for article in articles]
        else:
            # If no articles are found, display a message including the search term
            return html.P(f"No articles found matching the search term: '{search_term}'.")
    else:
        # If there's an error with the request, display a generic error message
        return html.P("An error occurred while fetching search results.")







# Run the application
if __name__ == '__main__':
    app.run_server(debug=True)
