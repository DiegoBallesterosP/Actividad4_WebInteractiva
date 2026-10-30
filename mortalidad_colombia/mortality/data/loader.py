"""Read the processed files into the dataset the dashboard uses."""

import json
from dataclasses import dataclass
from functools import lru_cache

import pandas as pd

from mortality.config import (
    AGE_GROUPS,
    CAUSES_FILE,
    DEATHS_FILE,
    GEOJSON_FILE,
    HOMICIDE_CODE_PREFIX,
    MUNICIPALITIES_FILE,
    SEX_LABELS,
)

AGE_GROUP_LABELS = [category for category, *_ in AGE_GROUPS]
AGE_GROUP_BY_CODE = {
    code: category
    for category, first_code, last_code, _ in AGE_GROUPS
    for code in range(first_code, last_code + 1)
}


@dataclass(frozen=True)
class Dataset:
    deaths: pd.DataFrame
    departments: dict
    cause_names: dict
    geojson: dict


def city_label(municipality, department):
    """Append the department, since several municipalities share the same name."""
    return municipality if municipality == department else f"{municipality} ({department})"


def _load_deaths(municipalities):
    """Build one row per death with readable labels.

    Labels and the homicide flag are worked out once here, so a filter
    change only needs to count rows.
    """
    raw = pd.read_csv(
        DEATHS_FILE,
        dtype={"municipality_code": str, "department_code": str, "cause_code": str},
    )
    cities = dict(zip(
        municipalities["municipality_code"],
        map(city_label, municipalities["municipality"], municipalities["department"]),
    ))
    departments = dict(zip(municipalities["department_code"], municipalities["department"]))

    return pd.DataFrame({
        "department_code": raw["department_code"].astype("category"),
        "department": raw["department_code"].map(departments).astype("category"),
        "city": raw["municipality_code"].map(cities).astype("category"),
        "month": raw["month"].astype("int8"),
        "sex": raw["sex_code"].map(SEX_LABELS).astype("category"),
        "age_group": pd.Categorical(raw["age_code"].map(AGE_GROUP_BY_CODE), categories=AGE_GROUP_LABELS),
        "cause_code": raw["cause_code"].astype("category"),
        "firearm_homicide": raw["cause_code"].str.startswith(HOMICIDE_CODE_PREFIX),
    })


@lru_cache(maxsize=1)
def load_dataset():
    municipalities = pd.read_csv(MUNICIPALITIES_FILE, dtype=str)
    departments = (
        municipalities.drop_duplicates("department_code")
        .sort_values("department")
        .set_index("department_code")["department"]
        .to_dict()
    )
    causes = pd.read_csv(CAUSES_FILE, dtype=str)
    with open(GEOJSON_FILE, encoding="utf-8") as file:
        geojson = json.load(file)

    return Dataset(
        deaths=_load_deaths(municipalities),
        departments=departments,
        cause_names=dict(zip(causes["code"], causes["name"])),
        geojson=geojson,
    )
