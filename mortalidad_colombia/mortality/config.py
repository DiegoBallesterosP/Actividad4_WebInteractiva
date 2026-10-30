"""Paths, page texts and DANE reference tables used across the app."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

DEATHS_FILE = PROCESSED_DIR / "deaths_2019.csv.gz"
CAUSES_FILE = PROCESSED_DIR / "causes.csv"
MUNICIPALITIES_FILE = PROCESSED_DIR / "municipalities.csv"
GEOJSON_FILE = PROCESSED_DIR / "colombia_departments.geojson"

APP_TITLE = "Mortalidad en Colombia 2019"
APP_SUBTITLE = "Análisis interactivo de las defunciones no fetales registradas por el DANE"
DATA_SOURCE = "Fuente: DANE, Estadísticas Vitales (EEVV) 2019"

AUTHOR = {
    "name": "Diego Fernando Pulido Ballesteros",
    "subject": "Aplicaciones 1",
    "program": "Maestría en Inteligencia Artificial",
    "university": "Universidad de La Salle",
}

HOMICIDE_CODE_PREFIX = "X95"

TOP_VIOLENT_CITIES = 5
LOWEST_MORTALITY_CITIES = 10
TOP_CAUSES = 10

MONTH_NAMES = (
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
)

SEX_LABELS = {1: "Hombre", 2: "Mujer", 3: "Indeterminado"}
MALE = SEX_LABELS[1]

AGE_GROUPS = (
    ("Mortalidad neonatal", 0, 4, "Menor de 1 mes"),
    ("Mortalidad infantil", 5, 6, "1 a 11 meses"),
    ("Primera infancia", 7, 8, "1 a 4 años"),
    ("Niñez", 9, 10, "5 a 14 años"),
    ("Adolescencia", 11, 11, "15 a 19 años"),
    ("Juventud", 12, 13, "20 a 29 años"),
    ("Adultez temprana", 14, 16, "30 a 44 años"),
    ("Adultez intermedia", 17, 19, "45 a 59 años"),
    ("Vejez", 20, 24, "60 a 84 años"),
    ("Longevidad / Centenarios", 25, 28, "85 a 100+ años"),
    ("Edad desconocida", 29, 29, "Sin información"),
)
