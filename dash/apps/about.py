import dash_bootstrap_components as dbc
from dash import dcc

from utils.colors import custom_colors

# Read the content of about.md
with open("content/about.md", "r") as file:
    about_content = file.read()

# Create the layout for the about page
layout = dbc.Container(
    [
        dcc.Markdown(
            children=about_content,
            style={"color": custom_colors["dark-blue"]},
            dangerously_allow_html=True,  # Allow rendering HTML tags
        )
    ]
)
