from dash import html
import dash_bootstrap_components as dbc
from dash import dcc

from utils.input_components import article_id_input
from utils.colors import custom_colors


# Read the content of home.md
with open("content/home.md", "r") as file:
    home_content = file.read()


# Create the layout for the home page
layout = dbc.Container(
    [
        html.H1(
            "Peptide Digest",
            style={"textAlign": "center", "color": custom_colors["dark-blue"]},
        ),
        dcc.Markdown(
            children=home_content,
            style={"color": custom_colors["dark-blue"]},
        ),
        html.Hr(),
        article_id_input,  # The input section with the submit button
        html.Div(
            id="article-info",
            style={"color": custom_colors["dark-blue"]},
        ),
    ],
    className="mt-4",
)
