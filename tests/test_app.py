import unittest

import pandas as pd

import app


class YouBikeAnalysisTests(unittest.TestCase):
    def test_district_options_include_all_13_values(self):
        expected_districts = [
            "中山區",
            "中正區",
            "信義區",
            "內湖區",
            "北投區",
            "南港區",
            "士林區",
            "大同區",
            "大安區",
            "文山區",
            "松山區",
            "臺大公館校區",
            "萬華區",
        ]

        self.assertEqual(app.行政區們, expected_districts)

    def assert_district_period_statistics(self, district, expected_rows):
        district_data = app.df.loc[
            (app.df["sarea"] == district) & app.df["analysis_included"]
        ]
        table = app.各時段空站統計(district_data)
        actual_rows = list(
            table[["資料時段", "站點總數", "空站數", "空站比例（%）"]].itertuples(
                index=False, name=None
            )
        )

        self.assertEqual(actual_rows, expected_rows)

    def test_daan_district_statistics_for_each_period(self):
        self.assert_district_period_statistics(
            "大安區",
            [
                ("09/30 00:31", 213, 18, 8.5),
                ("10/01 10:02", 213, 39, 18.3),
                ("10/07 15:40", 214, 10, 4.7),
            ],
        )

    def test_zhongshan_district_statistics_for_each_period(self):
        self.assert_district_period_statistics(
            "中山區",
            [
                ("09/30 00:31", 199, 8, 4.0),
                ("10/01 10:02", 199, 11, 5.5),
                ("10/07 15:40", 201, 3, 1.5),
            ],
        )

    def test_district_without_included_sites_has_undefined_rates(self):
        district_data = app.df.loc[
            (app.df["sarea"] == "臺大公館校區") & app.df["analysis_included"]
        ]
        table = app.各時段空站統計(district_data)

        self.assertEqual(table["資料時段"].tolist(), app.時段們)
        self.assertEqual(table["站點總數"].tolist(), [0] * len(app.時段們))
        self.assertEqual(table["空站數"].tolist(), [0] * len(app.時段們))
        self.assertTrue(table["空站比例（%）"].isna().all())

    def test_original_threshold_analysis_keeps_inclusive_boundary(self):
        data = pd.DataFrame(
            {
                "sno": ["a", "b", "c", "d"],
                "sarea": ["甲區", "甲區", "乙區", "乙區"],
                "available_rent_bikes": [0, 2, 1, 3],
            }
        )

        no_bikes = app.各區空站比例(data, 0).set_index("sarea")
        self.assertEqual(no_bikes.loc["甲區", "站數"], 2)
        self.assertEqual(no_bikes.loc["甲區", "空站數"], 1)
        self.assertEqual(no_bikes.loc["甲區", "空站比例"], 0.5)
        self.assertEqual(no_bikes.loc["乙區", "空站數"], 0)
        self.assertEqual(no_bikes.loc["乙區", "空站比例"], 0.0)

        two_bikes = app.各區空站比例(data, 2).set_index("sarea")
        self.assertEqual(two_bikes.loc["甲區", "空站數"], 2)
        self.assertEqual(two_bikes.loc["甲區", "空站比例"], 1.0)
        self.assertEqual(two_bikes.loc["乙區", "空站數"], 1)
        self.assertEqual(two_bikes.loc["乙區", "空站比例"], 0.5)


if __name__ == "__main__":
    unittest.main()