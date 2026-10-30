"""Page structure: header, filters, summary cards and chart grid."""

from dash import dash_table, dcc, html

from mortality import analytics
from mortality.config import APP_SUBTITLE, APP_TITLE, AUTHOR, DATA_SOURCE, MONTH_NAMES, SEX_LABELS
from mortality.ui import charts
from mortality.ui.theme import GRAPH_CONFIG, PRIMARY, TABLE_STYLE

ALL_SEXES = list(SEX_LABELS.values())
FULL_YEAR = [1, 12]
LOADING_DELAY_MS = 400

KPI_CARDS = (
    ("kpi-total", "Total de defunciones"),
    ("kpi-firearm-homicides", "Homicidios por arma de fuego (X95)"),
    ("kpi-male-share", "Proporción de hombres"),
    ("kpi-peak-month", "Mes con más defunciones"),
)

CAUSES_COLUMNS = [
    {"name": "#", "id": "rank"},
    {"name": "Código CIE-10", "id": "code"},
    {"name": "Causa de muerte", "id": "name"},
    {"name": "Total de casos", "id": "deaths", "type": "numeric",
     "format": {"specifier": ",d", "locale": {"group": ".", "decimal": ","}}},
]


def _header():
    return html.Header(className="header", children=[
        html.Div([html.H1(APP_TITLE), html.P(APP_SUBTITLE)]),
        html.Div(className="header__author", children=[
            html.Strong(AUTHOR["name"]),
            html.Span(f'{AUTHOR["subject"]} · {AUTHOR["program"]}'),
            html.Span(AUTHOR["university"]),
        ]),
    ])


def _labeled_control(label, control):
    return html.Div([html.Label(label, className="filter__label"), control])


def _filters(departments):
    department_options = [{"label": "Todos los departamentos", "value": analytics.ALL_DEPARTMENTS}] + [
        {"label": name, "value": code} for code, name in departments.items()
    ]
    return html.Section(className="card filters", children=[
        _labeled_control("Departamento", dcc.Dropdown(
            id="department-filter", options=department_options,
            value=analytics.ALL_DEPARTMENTS, clearable=False,
        )),
        _labeled_control("Sexo", dcc.Checklist(
            id="sex-filter", options=ALL_SEXES, value=ALL_SEXES, inline=True,
        )),
        _labeled_control("Meses", dcc.RangeSlider(
            id="month-filter", min=1, max=12, step=1, value=FULL_YEAR, allowCross=False,
            marks={number: name[:3] for number, name in enumerate(MONTH_NAMES, start=1)},
        )),
        html.Button("Restablecer filtros", id="reset-filters", className="button"),
        html.P("Consejo: haga clic en un departamento del mapa para filtrar por él.", className="filters__hint"),
    ])


def _kpi_row():
    return html.Section(className="kpis", children=[
        html.Div(className="card kpi", children=[
            html.Span(label, className="kpi__label"),
            html.Strong(id=element_id, className="kpi__value"),
        ])
        for element_id, label in KPI_CARDS
    ])


def _card(content, wide=False, note=None):
    children = [dcc.Loading(content, type="dot", color=PRIMARY, delay_show=LOADING_DELAY_MS)]
    if note:
        children.append(html.P(note, className="card__note"))
    return html.Div(className="card chart chart--wide" if wide else "card chart", children=children)


def _graph(graph_id, figure=None):
    return dcc.Graph(id=graph_id, config=GRAPH_CONFIG, figure=figure or {})


def _causes_table():
    return html.Div([
        html.H3("10 principales causas de muerte", className="card__title"),
        dash_table.DataTable(
            id="causes-table",
            columns=CAUSES_COLUMNS,
            style_cell_conditional=[
                {"if": {"column_id": "rank"}, "width": "36px", "textAlign": "center"},
                {"if": {"column_id": "code"}, "width": "110px"},
                {"if": {"column_id": "deaths"}, "width": "120px", "textAlign": "right"},
            ],
            **TABLE_STYLE,
        ),
    ])


def build_layout(dataset):
    map_figure = charts.department_map(
        analytics.deaths_by_department(dataset.deaths, dataset.departments), dataset.geojson,
    )
    return html.Div([
        _header(),
        html.Main(className="content", children=[
            _filters(dataset.departments),
            _kpi_row(),
            html.Section(className="grid", children=[
                _card(_graph("map-graph", map_figure)),
                _card(_graph("monthly-graph")),
                _card(_graph("violent-cities-graph")),
                _card(
                    _graph("lowest-cities-graph"),
                    note="Se usa el total de defunciones porque los datos no incluyen población. "
                         "Los empates se ordenan alfabéticamente.",
                ),
                _card(_causes_table(), wide=True, note="Ordenadas de mayor a menor número de casos."),
                _card(_graph("age-graph"), wide=True),
                _card(_graph("sex-department-graph"), wide=True),
            ]),
        ]),
        html.Footer(DATA_SOURCE, className="footer"),
    ])
