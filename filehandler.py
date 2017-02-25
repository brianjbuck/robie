import csv
import sys
import urllib.error
import urllib.request


from scheduleitem import ScheduleItem
from team import Team


def read(uri):
    """Open a File or a Web URL"""
    if uri.startswith('http://') or uri.startswith('https://'):
        return open_url(uri)
    else:
        return open_local_file(uri)


def open_url(url):
    """Return the game file data."""
    with urllib.request.urlopen(url) as response:
        if response.status != 200:
            msg = 'Status {}. Could Not Open URL {}. Reason: {}'
            raise urllib.error.HTTPError(
                msg.format(response.status, url, response.msg)
            )
        encoding = sys.getdefaultencoding()
        return [line.decode(encoding) for line in response.readlines()]


def open_local_file(uri):
    """Return the games file data as an array"""
    with open(uri, 'r') as f:
        return f.readlines()


def load_schedules(uri):
    data = read(uri)
    return [ScheduleItem.from_str(line) for line in data]


def load_teams_data(data_file):
    with open(data_file, 'r') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # Skip the header row
        return [Team(row[0], row[2], row[3]) for row in reader]
