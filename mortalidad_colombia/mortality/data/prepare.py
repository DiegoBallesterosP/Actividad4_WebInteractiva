"""Convert the raw DANE files into the small, clean files the app reads.

The mortality workbook is about 19 MB and takes around 20 s to read, so the
cleaning runs once here rather than on every server start.

Run from the project root:
    python -m mortality.data.prepare
"""

import json

import pandas as pd

from mortality.config import (
    CAUSES_FILE,
    DEATHS_FILE,
    GEOJSON_FILE,
    MUNICIPALITIES_FILE,
    PROCESSED_DIR,
    RAW_DIR,
)

DEATH_COLUMN_RENAMES = {
    "COD_DANE": "municipality_code",
    "COD_DEPARTAMENTO": "department_code",
    "MES": "month",
    "SEXO": "sex_code",
    "GRUPO_EDAD1": "age_code",
    "COD_MUERTE": "cause_code",
}
LOWERCASE_WORDS = {"de", "del", "la", "las", "los", "y", "el"}
DEPARTMENT_ALIASES = {"88": "San Andrés y Providencia"}
MISSING_MUNICIPALITIES = [
    {"municipality_code": "94663", "municipality": "Mapiripana", "department_code": "94"},
]
COORDINATE_DECIMALS = 4


def to_display_name(raw_name):
    """'NORTE DE SANTANDER' -> 'Norte de Santander'."""
    words = raw_name.strip().lower().split()
    return " ".join(
        word if index > 0 and word in LOWERCASE_WORDS else word.title()
        for index, word in enumerate(words)
    )


def to_sentence_case(text):
    """'Tumor Maligno De La Prostata [VIH]' -> 'Tumor maligno de la prostata [VIH]'."""
    words = [word if word.isupper() and len(word) > 1 else word.lower() for word in text.split()]
    sentence = " ".join(words)
    return sentence[:1].upper() + sentence[1:]


def prepare_deaths():
    deaths = pd.read_excel(
        RAW_DIR / "NoFetal2019.xlsx",
        sheet_name="No_Fetales_2019",
        usecols=list(DEATH_COLUMN_RENAMES),
        dtype={"COD_DANE": str, "COD_DEPARTAMENTO": str, "COD_MUERTE": str},
    ).rename(columns=DEATH_COLUMN_RENAMES)
    deaths["cause_code"] = deaths["cause_code"].str.strip()
    deaths.to_csv(DEATHS_FILE, index=False, compression="gzip")
    return deaths


def prepare_causes(used_codes):
    """Keep only the ICD-10 codes (3 or 4 characters) that appear in the data."""
    catalog = pd.read_excel(RAW_DIR / "CodigosDeMuerte.xlsx", sheet_name="Final", header=8, dtype=str)
    catalog = catalog.iloc[:, 2:6].dropna()
    catalog.columns = ["code3", "name3", "code4", "name4"]

    causes = pd.concat([
        pd.DataFrame({"code": catalog["code4"].str.strip(), "name": catalog["name4"].str.strip()}),
        pd.DataFrame({"code": catalog["code3"].str.strip(), "name": catalog["name3"].map(to_sentence_case)}),
    ]).drop_duplicates("code")
    causes = causes[causes["code"].isin(used_codes)]
    causes.to_csv(CAUSES_FILE, index=False)
    return causes


def prepare_municipalities():
    divipola = pd.read_excel(RAW_DIR / "Divipola.xlsx", sheet_name="Hoja3", header=1, dtype=str)
    divipola = divipola.iloc[:, :4].dropna()
    divipola.columns = ["department_code", "department", "municipality_code", "municipality"]

    departments = {
        code: DEPARTMENT_ALIASES.get(code, to_display_name(name))
        for code, name in zip(divipola["department_code"], divipola["department"])
    }
    municipalities = pd.concat([
        pd.DataFrame({
            "municipality_code": divipola["municipality_code"],
            "municipality": divipola["municipality"].map(to_display_name),
            "department_code": divipola["department_code"],
        }),
        pd.DataFrame(MISSING_MUNICIPALITIES),
    ], ignore_index=True)
    municipalities["department"] = municipalities["department_code"].map(departments)
    municipalities.to_csv(MUNICIPALITIES_FILE, index=False)
    return municipalities


def _round_coordinates(value):
    if isinstance(value, list):
        return [_round_coordinates(item) for item in value]
    return round(value, COORDINATE_DECIMALS)


def prepare_geojson():
    """Keep only the department code and round the coordinates to shrink the file."""
    with open(RAW_DIR / "colombia_departamentos.geo.json", encoding="utf-8") as file:
        geojson = json.load(file)
    for feature in geojson["features"]:
        feature["properties"] = {"DPTO": feature["properties"]["DPTO"]}
        feature["geometry"]["coordinates"] = _round_coordinates(feature["geometry"]["coordinates"])
    with open(GEOJSON_FILE, "w", encoding="utf-8") as file:
        json.dump(geojson, file, separators=(",", ":"))
    return geojson


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    deaths = prepare_deaths()
    print(f"Defunciones: {len(deaths)} registros")
    print(f"Causas: {len(prepare_causes(set(deaths['cause_code'])))} códigos")
    print(f"Municipios: {len(prepare_municipalities())} registros")
    print(f"Departamentos en el mapa: {len(prepare_geojson()['features'])}")


if __name__ == "__main__":
    main()
