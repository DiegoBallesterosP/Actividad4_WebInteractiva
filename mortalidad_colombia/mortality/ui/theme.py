"""Colors, fonts and the Plotly template shared by every chart.

assets/styles.css uses the same palette for the rest of the page.
"""

import plotly.graph_objects as go

PRIMARY = "#1f4e79"
ACCENT = "#c0392b"
TEXT = "#1d2733"
MUTED = "#5b6b7f"
GRID = "#e3e8ef"
STRIPE = "#f6f8fb"
FONT_FAMILY = "Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"

SEX_COLORS = {"Hombre": "#2e6aa3", "Mujer": "#d1495b", "Indeterminado": "#9aa5b1"}
SEQUENTIAL_SCALE = "Blues"
QUALITATIVE_PALETTE = (
    "#1f4e79", "#2e6aa3", "#4a90c2", "#7fb3d5", "#a9cce3",
    "#d1495b", "#e8797f", "#f0a6a0", "#9aa5b1", "#c8d1db",
)

_AXIS_STYLE = {"gridcolor": GRID, "zerolinecolor": GRID, "automargin": True}

PLOTLY_TEMPLATE = go.layout.Template(layout={
    "font": {"family": FONT_FAMILY, "size": 12, "color": TEXT},
    "title": {"x": 0.01, "xanchor": "left", "font": {"size": 16, "color": TEXT}},
    "paper_bgcolor": "white",
    "plot_bgcolor": "white",
    "margin": {"l": 16, "r": 16, "t": 56, "b": 16},
    "separators": ",.",
    "hoverlabel": {"font": {"family": FONT_FAMILY}},
    "xaxis": _AXIS_STYLE,
    "yaxis": _AXIS_STYLE,
})

GRAPH_CONFIG = {"displaylogo": False, "responsive": True}

TABLE_STYLE = {
    "style_as_list_view": True,
    "style_header": {"backgroundColor": PRIMARY, "color": "white", "fontWeight": "600", "border": "none"},
    "style_cell": {
        "fontFamily": FONT_FAMILY, "fontSize": 13, "padding": "10px 12px", "textAlign": "left",
        "whiteSpace": "normal", "height": "auto", "border": "none", "borderBottom": f"1px solid {GRID}",
    },
    "style_data_conditional": [{"if": {"row_index": "odd"}, "backgroundColor": STRIPE}],
}
