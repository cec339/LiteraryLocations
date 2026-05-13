import unittest

from utils.data_loader import (
    REQUIRED_COLUMNS,
    _ordinal,
    get_dataset_stats,
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

    def test_loaded_data_integrity(self):
        self.assertFalse(self.books.empty)
        self.assertEqual(list(self.books.columns), REQUIRED_COLUMNS)
        self.assertEqual(len(self.books), len(self.books.drop_duplicates(subset=["title", "author"])))
        self.assertTrue(self.books["setting_latitude"].between(-90, 90).all())
        self.assertTrue(self.books["setting_longitude"].between(-180, 180).all())

    def test_why_here_is_string_column(self):
        self.assertIn("why_here", self.books.columns)
        self.assertTrue(self.books["why_here"].apply(lambda v: isinstance(v, str)).all())


if __name__ == "__main__":
    unittest.main()
