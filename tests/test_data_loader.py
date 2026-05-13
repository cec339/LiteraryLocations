import unittest

from utils.data_loader import (
    REQUIRED_COLUMNS,
    _ordinal,
    determine_location_type_and_coordinates,
    get_dataset_stats,
    get_publication_coordinates,
    load_book_data,
    search_books,
)


class DataLoaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.books = load_book_data()

    def test_search_treats_regex_characters_as_literals(self):
        for query in ["[", "*", "("]:
            with self.subTest(query=query):
                search_books(query, self.books)

        dot_results = search_books(".", self.books)
        self.assertGreater(len(dot_results), 0)
        self.assertLess(len(dot_results), len(self.books))

    def test_century_ordinals(self):
        cases = {
            -20: "20th BCE",
            -1: "1st BCE",
            1: "1st",
            11: "11th",
            13: "13th",
            21: "21st",
        }
        for century, expected in cases.items():
            with self.subTest(century=century):
                self.assertEqual(_ordinal(century), expected)

    def test_dataset_stats_use_correct_century_range(self):
        stats = get_dataset_stats(self.books)
        self.assertEqual(stats["century_range"], "20th BCE to 21st")

    def test_location_classification_handles_fictional_and_real_names(self):
        atlantis_book = {
            "author": "Unknown Author",
            "year": 2000,
            "location": {"name": "Atlantis", "coordinates": [31.0, -24.0]},
        }
        coords, location_type = determine_location_type_and_coordinates(atlantis_book)
        self.assertEqual(coords, [40.7128, -74.006])
        self.assertEqual(location_type, "publication")

        sweden_book = {
            "author": "Unknown Author",
            "year": 2000,
            "location": {"name": "Sweden", "coordinates": [59.3293, 18.0686]},
        }
        coords, location_type = determine_location_type_and_coordinates(sweden_book)
        self.assertEqual(coords, [59.3293, 18.0686])
        self.assertEqual(location_type, "primary")

    def test_location_classification_rejects_missing_and_null_island_coordinates(self):
        missing_book = {
            "author": "Jane Austen",
            "year": 1813,
            "location": {"name": "Hertfordshire", "coordinates": None},
        }
        coords, location_type = determine_location_type_and_coordinates(missing_book)
        self.assertEqual(coords, [50.9097, -1.4044])
        self.assertEqual(location_type, "publication")

        null_island_book = {
            "author": "Jane Austen",
            "year": 1813,
            "location": {"name": "Hertfordshire", "coordinates": [0, 0]},
        }
        coords, location_type = determine_location_type_and_coordinates(null_island_book)
        self.assertEqual(coords, [50.9097, -1.4044])
        self.assertEqual(location_type, "publication")

    def test_publication_coordinate_fallbacks(self):
        self.assertEqual(get_publication_coordinates("Emily Brontë", 1847)[0], [53.8008, -1.5491])
        self.assertEqual(get_publication_coordinates("Unknown Ancient", 1200)[0], [41.9028, 12.4964])
        self.assertEqual(get_publication_coordinates("Unknown Modern", 2000)[0], [40.7128, -74.006])

    def test_loaded_data_integrity(self):
        self.assertFalse(self.books.empty)
        self.assertEqual(list(self.books.columns), REQUIRED_COLUMNS)
        self.assertEqual(len(self.books), len(self.books.drop_duplicates(subset=["title", "author"])))
        self.assertTrue(self.books["setting_latitude"].between(-90, 90).all())
        self.assertTrue(self.books["setting_longitude"].between(-180, 180).all())


if __name__ == "__main__":
    unittest.main()
