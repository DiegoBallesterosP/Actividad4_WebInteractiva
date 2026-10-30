"""Aggregations behind each chart.

Each function takes an already filtered deaths DataFrame and returns a small
table, which keeps the logic testable without Dash.
"""

import pandas as pd

from mortality.config import LOWEST_MORTALITY_CITIES, MALE, SEX_LABELS, TOP_CAUSES, TOP_VIOLENT_CITIES

ALL_DEPARTMENTS = "ALL"


def filter_deaths(deaths, department=ALL_DEPARTMENTS, sexes=None, month_range=(1, 12)):
    mask = deaths["month"].between(*month_range)
    if department != ALL_DEPARTMENTS:
        mask &= deaths["department_code"] == department
    if sexes is not None:
        mask &= deaths["sex"].isin(sexes)
    return deaths[mask]


def _count(series):
    """Value counts without the empty categories that pandas includes as zeros."""
    counts = series.value_counts()
    return counts[counts > 0]


def summary(deaths):
    total = len(deaths)
    return {
        "total": total,
        "firearm_homicides": int(deaths["firearm_homicide"].sum()),
        "male_share": (deaths["sex"] == MALE).mean() if total else 0.0,
        "peak_month": int(deaths["month"].mode().iloc[0]) if total else None,
    }


def deaths_by_department(deaths, departments):
    """Totals per department in the order of `departments`, zeros included.

    Keeping the order fixed lets the map update just its values.
    """
    counts = deaths["department_code"].value_counts()
    return pd.DataFrame({
        "department_code": list(departments),
        "department": list(departments.values()),
        "deaths": [int(counts.get(code, 0)) for code in departments],
    })


def deaths_by_month(deaths):
    counts = deaths["month"].value_counts().reindex(range(1, 13), fill_value=0)
    return pd.DataFrame({"month": counts.index, "deaths": counts.to_numpy()})


def _deaths_by_city(deaths):
    counts = _count(deaths["city"])
    return pd.DataFrame({"city": counts.index.astype(str), "deaths": counts.to_numpy()})


def top_violent_cities(deaths, limit=TOP_VIOLENT_CITIES):
    """Cities with the most firearm homicides (ICD-10 X95)."""
    cities = _deaths_by_city(deaths[deaths["firearm_homicide"]])
    return cities.sort_values(["deaths", "city"], ascending=[False, True]).head(limit).reset_index(drop=True)


def lowest_mortality_cities(deaths, limit=LOWEST_MORTALITY_CITIES):
    """Cities with the fewest registered deaths; ties are broken alphabetically."""
    cities = _deaths_by_city(deaths)
    return cities.sort_values(["deaths", "city"]).head(limit).reset_index(drop=True)


def top_causes(deaths, cause_names, limit=TOP_CAUSES):
    counts = _count(deaths["cause_code"]).head(limit)
    codes = counts.index.astype(str)
    return pd.DataFrame({
        "rank": range(1, len(codes) + 1),
        "code": codes,
        "name": [cause_names.get(code, "Sin descripción") for code in codes],
        "deaths": counts.to_numpy(),
    })


def deaths_by_department_and_sex(deaths):
    """One column per sex, with departments sorted from fewest to most deaths."""
    table = (
        deaths.groupby(["department", "sex"], observed=True).size()
        .unstack(fill_value=0)
        .reindex(columns=list(SEX_LABELS.values()), fill_value=0)
    )
    return table.loc[table.sum(axis=1).sort_values().index].reset_index()


def deaths_by_age_group(deaths):
    counts = deaths["age_group"].value_counts(sort=False)
    return pd.DataFrame({"age_group": counts.index.astype(str), "deaths": counts.to_numpy()})
