"""Plotly figures, one per chart.

Each function takes a table from mortality.analytics and only handles how it
looks. They use graph_objects rather than plotly.express, which adds about
20 ms per chart: enough to notice when a filter redraws six of them.
"""

import plotly.graph_objects as go
from dash import Patch

from mortality.config import AGE_GROUPS, HOMICIDE_CODE_PREFIX, MONTH_NAMES
from mortality.ui.theme import (
    ACCENT,
    MUTED,
    PLOTLY_TEMPLATE,
    PRIMARY,
    QUALITATIVE_PALETTE,
    SEQUENTIAL_SCALE,
    SEX_COLORS,
)

DEATHS_LABEL = "Número de defunciones"
EMPTY_MESSAGE = "No hay defunciones para los filtros seleccionados"
DEFAULT_HEIGHT = 420
TALL_HEIGHT = 520
STACKED_ROW_HEIGHT = 24
MAP_LONGITUDE_RANGE = [-82.0, -66.5]
MAP_LATITUDE_RANGE = [-4.4, 13.6]
AGE_AXIS_LABELS = {category: f"{category}<br>({age_range})" for category, _, _, age_range in AGE_GROUPS}


def _figure(data, title, height=DEFAULT_HEIGHT, **layout):
    return go.Figure(data=data, layout={
        "template": PLOTLY_TEMPLATE, "title": {"text": title}, "height": height, **layout,
    })


def _axis(title, **options):
    return {"title": {"text": title}, **options}


def _empty_figure(title):
    return _figure(
        [], title,
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[{
            "text": EMPTY_MESSAGE, "showarrow": False, "font": {"size": 14, "color": MUTED},
            "xref": "paper", "yref": "paper", "x": 0.5, "y": 0.5,
        }],
    )


def department_map(table, geojson):
    """Full map with the department shapes, built once when the page loads."""
    choropleth = go.Choropleth(
        geojson=geojson,
        featureidkey="properties.DPTO",
        locations=table["department_code"],
        z=table["deaths"],
        text=table["department"],
        coloraxis="coloraxis",
        marker={"line": {"color": "white", "width": 0.6}},
        hovertemplate="<b>%{text}</b><br>%{z:,d} defunciones<extra></extra>",
    )
    return _figure(
        [choropleth], "Total de defunciones por departamento", TALL_HEIGHT,
        coloraxis={
            "colorscale": SEQUENTIAL_SCALE, "cmin": 0,
            "colorbar": {"title": {"text": "Defunciones"}, "thickness": 14},
        },
        geo={
            "visible": False,
            "projection": {"type": "mercator"},
            "lonaxis": {"range": MAP_LONGITUDE_RANGE},
            "lataxis": {"range": MAP_LATITUDE_RANGE},
        },
    )


def department_map_update(table):
    """Send only the new totals instead of the ~600 KB of shapes again."""
    patch = Patch()
    patch["data"][0]["z"] = table["deaths"].tolist()
    return patch


def monthly_line(table):
    line = go.Scatter(
        x=[MONTH_NAMES[month - 1][:3] for month in table["month"]],
        y=table["deaths"],
        customdata=[MONTH_NAMES[month - 1] for month in table["month"]],
        mode="lines+markers",
        line={"color": PRIMARY, "width": 3},
        marker={"size": 8},
        hovertemplate="%{customdata}<br>%{y:,d} defunciones<extra></extra>",
    )
    return _figure(
        [line], "Total de defunciones por mes", TALL_HEIGHT,
        xaxis=_axis("Mes"),
        yaxis=_axis(DEATHS_LABEL, rangemode="tozero"),
    )


def violent_cities_bar(table):
    title = f"5 ciudades más violentas: homicidios por arma de fuego ({HOMICIDE_CODE_PREFIX})"
    if table.empty:
        return _empty_figure(title)
    ordered = table.iloc[::-1]
    bar = go.Bar(
        x=ordered["deaths"], y=ordered["city"], orientation="h",
        text=ordered["deaths"], texttemplate="%{text:,d}", textposition="outside", cliponaxis=False,
        marker_color=ACCENT,
        hovertemplate="%{y}<br>%{x:,d} homicidios<extra></extra>",
    )
    return _figure([bar], title, xaxis=_axis("Número de homicidios"), yaxis=_axis("Ciudad"))


def lowest_mortality_pie(table):
    title = "10 ciudades con menor número de defunciones"
    if table.empty:
        return _empty_figure(title)
    pie = go.Pie(
        labels=table["city"], values=table["deaths"], sort=False, textinfo="value",
        marker={"colors": QUALITATIVE_PALETTE, "line": {"color": "white", "width": 1.5}},
        hovertemplate="%{label}<br>%{value:,d} defunciones<extra></extra>",
    )
    return _figure([pie], title, legend={"title": {"text": "Ciudad"}, "font": {"size": 11}})


def sex_by_department_stacked(table):
    title = "Defunciones por sexo en cada departamento"
    if table.empty:
        return _empty_figure(title)
    bars = [
        go.Bar(
            name=sex, x=table[sex], y=table["department"], orientation="h", marker_color=color,
            hovertemplate="%{y}<br>" + sex + ": %{x:,d}<extra></extra>",
        )
        for sex, color in SEX_COLORS.items()
    ]
    return _figure(
        bars, title, max(320, STACKED_ROW_HEIGHT * len(table) + 140),
        barmode="stack",
        legend={"title": {"text": "Sexo"}, "orientation": "h", "traceorder": "normal",
                "y": 1.02, "yanchor": "bottom", "x": 1, "xanchor": "right"},
        xaxis=_axis(DEATHS_LABEL),
        yaxis=_axis("Departamento"),
    )


def age_histogram(table):
    title = "Distribución de defunciones por grupo de edad (GRUPO_EDAD1)"
    if table["deaths"].sum() == 0:
        return _empty_figure(title)
    labels = table["age_group"].map(AGE_AXIS_LABELS)
    histogram = go.Histogram(
        x=labels, y=table["deaths"], histfunc="sum",
        marker_color=PRIMARY,
        hovertemplate="%{x}<br>%{y:,d} defunciones<extra></extra>",
    )
    return _figure(
        [histogram], title, 460,
        bargap=0.08,
        xaxis=_axis("Grupo de edad", tickfont={"size": 11}, categoryorder="array", categoryarray=list(labels)),
        yaxis=_axis(DEATHS_LABEL),
    )
