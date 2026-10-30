"""Checks on the cleaning rules and on the processed data they produce."""

import unittest

from mortality import analytics
from mortality.data import load_dataset
from mortality.data.loader import AGE_GROUP_BY_CODE, city_label
from mortality.data.prepare import to_display_name, to_sentence_case

REAL_TOTAL_DEATHS = 244_355


class CleaningTests(unittest.TestCase):
    def test_display_names(self):
        self.assertEqual(to_display_name("NORTE DE SANTANDER"), "Norte de Santander")
        self.assertEqual(to_display_name("LA GUAJIRA"), "La Guajira")
        self.assertEqual(to_display_name("BOGOTÁ, D.C."), "Bogotá, D.C.")

    def test_sentence_case_keeps_acronyms(self):
        self.assertEqual(to_sentence_case("Tumor Maligno De La Prostata"), "Tumor maligno de la prostata")
        self.assertEqual(to_sentence_case("Infeccion Por [VIH]"), "Infeccion por [VIH]")

    def test_city_label(self):
        self.assertEqual(city_label("Medellín", "Antioquia"), "Medellín (Antioquia)")
        self.assertEqual(city_label("Bogotá, D.C.", "Bogotá, D.C."), "Bogotá, D.C.")

    def test_every_age_code_has_a_group(self):
        self.assertEqual(sorted(AGE_GROUP_BY_CODE), list(range(30)))
        self.assertEqual(AGE_GROUP_BY_CODE[4], "Mortalidad neonatal")
        self.assertEqual(AGE_GROUP_BY_CODE[5], "Mortalidad infantil")
        self.assertEqual(AGE_GROUP_BY_CODE[29], "Edad desconocida")


class DatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = load_dataset()
        cls.deaths = cls.dataset.deaths

    def test_every_record_is_loaded_and_labeled(self):
        self.assertEqual(len(self.deaths), REAL_TOTAL_DEATHS)
        self.assertEqual(int(self.deaths.isna().sum().sum()), 0)

    def test_totals_match_across_charts(self):
        sexes = analytics.deaths_by_department_and_sex(self.deaths)
        totals = (
            analytics.deaths_by_department(self.deaths, self.dataset.departments)["deaths"].sum(),
            analytics.deaths_by_month(self.deaths)["deaths"].sum(),
            analytics.deaths_by_age_group(self.deaths)["deaths"].sum(),
            sexes.drop(columns="department").to_numpy().sum(),
        )
        self.assertEqual(set(totals), {REAL_TOTAL_DEATHS})

    def test_every_department_has_a_map_shape(self):
        map_codes = {feature["properties"]["DPTO"] for feature in self.dataset.geojson["features"]}
        self.assertEqual(set(self.dataset.departments), map_codes)

    def test_every_cause_has_a_name(self):
        self.assertTrue(self.deaths["cause_code"].isin(self.dataset.cause_names.keys()).all())

    def test_empty_filter_returns_empty_tables(self):
        empty = analytics.filter_deaths(self.deaths, "97", ["Indeterminado"], (6, 6))
        self.assertTrue(analytics.top_causes(empty, self.dataset.cause_names).empty)
        self.assertTrue(analytics.lowest_mortality_cities(empty).empty)

    def test_known_results(self):
        self.assertEqual(analytics.summary(self.deaths)["firearm_homicides"], 9_273)
        self.assertEqual(analytics.top_violent_cities(self.deaths)["city"].iloc[0], "Santiago de Cali (Valle del Cauca)")
        self.assertEqual(analytics.top_causes(self.deaths, self.dataset.cause_names)["code"].iloc[0], "I219")


if __name__ == "__main__":
    unittest.main()
