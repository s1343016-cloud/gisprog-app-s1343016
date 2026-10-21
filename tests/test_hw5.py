import unittest
from unittest.mock import patch

from ipywidgets.widgets.widget import _instances

import app


class MapTests(unittest.TestCase):
    def test_replacing_map_releases_child_widgets(self):
        before = set(_instances)
        for _ in range(3):
            # 略過需要前端回覆的縮放，這裡只測圖層及控制項的資源釋放。
            with patch.object(app.leafmap.Map, "fit_bounds"):
                map_widget = app.建立地圖(app.篩選站點("大安區", "09/30 00:31"))
            if _ == 1:
                map_widget.remove(map_widget.controls[-1])
            app.關閉地圖(map_widget)
        self.assertEqual(set(_instances), before)

    def test_supply_class_boundaries(self):
        self.assertTrue(hasattr(app, "供應分級"), "尚未實作地圖分級")
        self.assertEqual(
            [app.供應分級(n) for n in [0, 1, 3, 4, 9, 10, 1000]],
            ["0 輛（空站）", "1–3 輛", "1–3 輛", "4–9 輛", "4–9 輛", "10 輛以上", "10 輛以上"],
        )
        for value in [-1, float("nan"), 1.5]:
            with self.assertRaises(ValueError):
                app.供應分級(value)

    def test_filters_and_geojson_use_same_stations(self):
        self.assertTrue(hasattr(app, "篩選站點"), "尚未實作地圖共用篩選")
        for district, period, expected in [
            ("大安區", "09/30 00:31", 213),
            ("中山區", "09/30 00:31", 199),
            ("大安區", "10/07 15:40", 214),
            ("臺大公館校區", "09/30 00:31", 0),
        ]:
            with self.subTest(district=district, period=period):
                rows = app.篩選站點(district, period)
                geo = app.轉成GeoJSON(rows)
                self.assertEqual(len(rows), expected)
                self.assertEqual(len(geo["features"]), expected)
                self.assertEqual(int(rows["分級"].value_counts().sum()), expected)
                if expected:
                    first = rows.iloc[0]
                    feature = geo["features"][0]
                    self.assertEqual(feature["geometry"]["coordinates"], [first.longitude, first.latitude])
                    self.assertEqual(feature["properties"]["站名"], first.sna)
                    self.assertEqual(feature["properties"]["可借車數"], int(first.available_rent_bikes))

    def test_reject_invalid_map_data(self):
        self.assertTrue(hasattr(app, "轉成GeoJSON"), "尚未實作 GeoJSON")
        row = app.df.loc[app.df["analysis_included"]].head(1)
        for column, value in [("latitude", 121), ("longitude", float("nan")), ("available_rent_bikes", -1)]:
            with self.subTest(column=column):
                invalid = row.assign(**{column: value})
                with self.assertRaises(ValueError):
                    app.轉成GeoJSON(invalid)


if __name__ == "__main__":
    unittest.main()
