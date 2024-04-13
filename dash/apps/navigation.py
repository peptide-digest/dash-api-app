from dash import html
import dash_bootstrap_components as dbc

from utils.colors import custom_colors

# Create the navigation bar
layout = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/")),
        dbc.NavItem(dbc.NavLink("Search", href="/search")),
        dbc.NavItem(dbc.NavLink("DB Search", href="/dbsearch")),
        dbc.NavItem(dbc.NavLink("About", href="/about")),
    ],
    brand=html.Div(
        [
            # Logo and title
            html.Img(src="assets/peptide_digest_logo.jpeg", height="40px"),
            html.Span("Peptide Digest", style={"marginLeft": "10px"}),
        ]
    ),
    brand_href="/",
    color=custom_colors["teal"],
    dark=True,
)
