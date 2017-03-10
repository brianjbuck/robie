import unittest

from robie import filehandler


class TestFileHandler(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_open_csv_file(self):
        schedule_items = filehandler.parse_schedules(uri='tests/data.csv')
        self.assertEquals(len(schedule_items), 34)

    def test_empty_csv_file(self):
        with self.assertRaises(ValueError):
            filehandler.parse_schedules(uri='tests/empty_data.csv')

    def test_empty_txt_file(self):
        with self.assertRaises(ValueError):
            filehandler.parse_schedules(uri='tests/empty_data.txt')