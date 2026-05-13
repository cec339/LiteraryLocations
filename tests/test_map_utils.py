import unittest

from utils.map_utils import create_base_map_html


class MapUtilsTests(unittest.TestCase):
    def test_base_map_html_includes_leaflet_and_cluster_assets(self):
        html = create_base_map_html()
        self.assertIn("leaflet", html.lower())
        self.assertIn("markercluster", html.lower())
        self.assertIn(".leaflet-top.leaflet-left", html)


if __name__ == "__main__":
    unittest.main()
