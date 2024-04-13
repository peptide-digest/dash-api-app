import dash
from dash import html
import dash_bootstrap_components as dbc

from utils.colors import custom_colors


layout = dbc.Navbar(
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
