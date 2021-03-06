import csv
import os
import sys
import urllib.error
import urllib.request

from robie.scheduleitem import ScheduleItem
from robie.team import Team


def read(uri, store_file=False):
    """Open a File or a Web URL"""
    if uri.startswith('http://') or uri.startswith('https://'):
        return open_url(uri, store_file=store_file)
    else:
        return open_local_file(uri)


def open_url(url, store_file=False):
    """Return the game file data."""
    with urllib.request.urlopen(url) as response:
        if response.status != 200:
            msg = (
                    f'Status {response.status}. Could Not Open URL {url}. '
                    f'Reason: {response.msg}'
                )
            raise urllib.error.HTTPError(
                url=url,
                code=response.status,
                msg=msg,
                hdrs={},
                fp=None
            )
        encoding = sys.getdefaultencoding()
        encoded_data = [line.decode(encoding) for line in response.readlines()]
        if store_file:
            write_local_file(url.split('/')[-1], encoded_data)
        return encoded_data


def write_local_file(file_name, data):
    file_path = os.path.join('data', 'gamesfiles', file_name)
    with open(file_path, 'w') as f:
        f.write(''.join(data))


def open_local_file(uri):
    """Return the games file data as an array"""
    file_name, ext = os.path.splitext(uri)
    if ext == '.csv':
        with open(uri, 'r') as csv_file:
            reader = csv.reader(csv_file)
            return [[col for col in row] for row in reader]
    else:
        with open(uri, 'r') as f:
            return f.readlines()


def parse_schedules(uri, store_file=False):
    """
    Detect if the data is in gamesfile format or from CSV (list of lists), then
    parse the data into list of dicts.
    """
    data = read(uri, store_file=store_file)
    if len(data):
        if isinstance(data[0], list):
            return [ScheduleItem.from_list(line) for line in data]
        elif isinstance(data[0], str):
            return [ScheduleItem.from_str(line) for line in data]
    else:
        raise ValueError('Data file didn\'t read correctly or was empty.')


def load_teams(path):
    with open(path, 'r') as f:
        return [Team(name.strip()) for name in f.readlines() if name.strip()]
