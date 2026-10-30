"""Callbacks: any filter change refreshes the whole dashboard."""

from dash import Input, Output, ctx, no_update

from mortality import analytics
from mortality.config import MONTH_NAMES
from mortality.ui import charts
from mortality.ui.layout import ALL_SEXES, FULL_YEAR


def _format_number(value):
    """Use a dot as the thousands separator, as in Spanish: 244355 -> '244.355'."""
    return f"{value:,}".replace(",", ".")


def register_callbacks(app, dataset):
    @app.callback(
        Output("kpi-total", "children"),
        Output("kpi-firearm-homicides", "children"),
        Output("kpi-male-share", "children"),
        Output("kpi-peak-month", "children"),
        Output("map-graph", "figure"),
        Output("monthly-graph", "figure"),
        Output("violent-cities-graph", "figure"),
        Output("lowest-cities-graph", "figure"),
        Output("causes-table", "data"),
        Output("sex-department-graph", "figure"),
        Output("age-graph", "figure"),
        Input("department-filter", "value"),
        Input("sex-filter", "value"),
        Input("month-filter", "value"),
    )
    def update_dashboard(department, sexes, month_range):
        deaths = analytics.filter_deaths(dataset.deaths, department, sexes, month_range)
        stats = analytics.summary(deaths)
        return (
            _format_number(stats["total"]),
            _format_number(stats["firearm_homicides"]),
            f"{stats['male_share']:.1%}",
            MONTH_NAMES[stats["peak_month"] - 1] if stats["peak_month"] else "-",
            charts.department_map_update(analytics.deaths_by_department(deaths, dataset.departments)),
            charts.monthly_line(analytics.deaths_by_month(deaths)),
            charts.violent_cities_bar(analytics.top_violent_cities(deaths)),
            charts.lowest_mortality_pie(analytics.lowest_mortality_cities(deaths)),
            analytics.top_causes(deaths, dataset.cause_names).to_dict("records"),
            charts.sex_by_department_stacked(analytics.deaths_by_department_and_sex(deaths)),
            charts.age_histogram(analytics.deaths_by_age_group(deaths)),
        )

    @app.callback(
        Output("department-filter", "value"),
        Output("sex-filter", "value"),
        Output("month-filter", "value"),
        Input("map-graph", "clickData"),
        Input("reset-filters", "n_clicks"),
        prevent_initial_call=True,
    )
    def update_filters(map_click, _reset_clicks):
        if ctx.triggered_id == "reset-filters":
            return analytics.ALL_DEPARTMENTS, ALL_SEXES, FULL_YEAR
        return map_click["points"][0]["location"], no_update, no_update
