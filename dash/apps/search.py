from dash import html
import dash_bootstrap_components as dbc

from utils.article_input import article_id_input
from utils.colors import custom_colors

# Create the layout for the search page
layout = dbc.Container(
    [
        html.H2("Search for Articles", style={"color": custom_colors["dark-blue"]}),
        article_id_input,
        html.Div(id="article-info", style={"color": custom_colors["dark-blue"]}),
    ]
)
