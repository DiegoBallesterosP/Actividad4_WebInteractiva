"""Aggregation tests on a small hand-made dataset."""

import unittest

import pandas as pd

from mortality import analytics
from mortality.ui import charts

DEPARTMENTS = {"05": "Antioquia", "11": "Bogotá, D.C.", "76": "Valle del Cauca"}


def sample_deaths():
    rows = [
        ("05", "Antioquia", "Medellín (Antioquia)", 1, "Hombre", "Juventud", "X954"),
        ("05", "Antioquia", "Medellín (Antioquia)", 1, "Hombre", "Juventud", "X959"),
        ("05", "Antioquia", "Abejorral (Antioquia)", 2, "Mujer", "Vejez", "I219"),
        ("11", "Bogotá, D.C.", "Bogotá, D.C.", 2, "Mujer", "Vejez", "I219"),
        ("11", "Bogotá, D.C.", "Bogotá, D.C.", 3, "Hombre", "Vejez", "X950"),
        ("76", "Valle del Cauca", "Santiago de Cali (Valle del Cauca)", 12, "Indeterminado", "Niñez", "C61"),
    ]
    deaths = pd.DataFrame(rows, columns=["department_code", "department", "city", "month",
                                         "sex", "age_group", "cause_code"])
    deaths["firearm_homicide"] = deaths["cause_code"].str.startswith("X95")
    return deaths


class AnalyticsTests(unittest.TestCase):
    def setUp(self):
        self.deaths = sample_deaths()

    def test_filters_combine(self):
        filtered = analytics.filter_deaths(self.deaths, "05", ["Hombre"], (1, 1))
        self.assertEqual(len(filtered), 2)

    def test_summary(self):
        stats = analytics.summary(self.deaths)
        self.assertEqual(stats["total"], 6)
        self.assertEqual(stats["firearm_homicides"], 3)
        self.assertEqual(stats["peak_month"], 1)
        self.assertAlmostEqual(stats["male_share"], 0.5)

    def test_departments_keep_order_and_zeros(self):
        table = analytics.deaths_by_department(self.deaths[self.deaths["department_code"] == "11"], DEPARTMENTS)
        self.assertEqual(table["department_code"].tolist(), list(DEPARTMENTS))
        self.assertEqual(table["deaths"].tolist(), [0, 2, 0])

    def test_month_series_has_twelve_months(self):
        months = analytics.deaths_by_month(self.deaths)
        self.assertEqual(len(months), 12)
        self.assertEqual(months["deaths"].sum(), 6)
        self.assertEqual(months.loc[months["month"] == 4, "deaths"].item(), 0)

    def test_violent_cities_only_use_x95(self):
        cities = analytics.top_violent_cities(self.deaths)
        self.assertEqual(cities["city"].tolist(), ["Medellín (Antioquia)", "Bogotá, D.C."])
        self.assertEqual(cities["deaths"].tolist(), [2, 1])

    def test_lowest_cities_break_ties_alphabetically(self):
        cities = analytics.lowest_mortality_cities(self.deaths, limit=2)
        self.assertEqual(cities["city"].tolist(), ["Abejorral (Antioquia)", "Santiago de Cali (Valle del Cauca)"])

    def test_top_causes_sorted_by_cases(self):
        causes = analytics.top_causes(self.deaths, {"I219": "Infarto"}, limit=2)
        self.assertEqual(causes["rank"].tolist(), [1, 2])
        self.assertEqual(causes.loc[0, ["code", "name", "deaths"]].tolist(), ["I219", "Infarto", 2])

    def test_sex_table_sorted_by_total(self):
        table = analytics.deaths_by_department_and_sex(self.deaths)
        self.assertEqual(table["department"].tolist()[-1], "Antioquia")
        self.assertEqual(table.columns.tolist(), ["department", "Hombre", "Mujer", "Indeterminado"])

    def test_empty_selection_still_renders(self):
        empty = analytics.filter_deaths(self.deaths, "05", [], (1, 12))
        self.assertIsNone(analytics.summary(empty)["peak_month"])
        self.assertTrue(analytics.top_violent_cities(empty).empty)
        self.assertTrue(analytics.deaths_by_department_and_sex(empty).empty)
        charts.violent_cities_bar(analytics.top_violent_cities(empty))
        charts.sex_by_department_stacked(analytics.deaths_by_department_and_sex(empty))


if __name__ == "__main__":
    unittest.main()
