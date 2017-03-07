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
            msg = 'Status {}. Could Not Open URL {}. Reason: {}'
            raise urllib.error.HTTPError(
                msg.format(response.status, url, response.msg)
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
    with open(uri, 'r') as f:
        return f.readlines()


def load_schedules(uri, store_file=False):
    data = read(uri, store_file=store_file)
    return [ScheduleItem.from_str(line) for line in data]


def load_teams(path):
    with open(path, 'r') as f:
        return [Team(name.strip()) for name in f.readlines() if name.strip()]
