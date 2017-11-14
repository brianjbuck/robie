import unittest
from unittest.mock import patch, MagicMock
import urllib

from robie import filehandler


class TestFileHandler(unittest.TestCase):
    def setUp(self):
        self.data_csv = 'tests/data.csv'

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

    @patch('urllib.request.urlopen')
    def test_filehandler_open_url(self, mock_urlopen):
        with open('tests/data.txt', 'rb') as f:
            data = f.readlines()
        cm = MagicMock()
        cm.status = 200
        cm.readlines.return_value = data
        cm.__enter__.return_value = cm
        mock_urlopen.return_value = cm

        schedule_items = filehandler.parse_schedules(
            uri='http://kenpom.com/cbbga17.txt'
        )
        self.assertEquals(len(schedule_items), 34)

    @patch('urllib.request.urlopen')
    def test_filehandler_open_url_status_not_200(self, mock_urlopen):
        cm = MagicMock()
        cm.status = 404
        cm.msg = 'Not found.'
        cm.__enter__.return_value = cm
        mock_urlopen.return_value = cm

        with self.assertRaises(urllib.error.HTTPError):
            filehandler.parse_schedules(uri='http://kenpom.com/cbbga17.txt')
