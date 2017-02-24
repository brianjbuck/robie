import csv
import sys
import urllib

from scheduleitem import ScheduleItem
from team import Team


def read(uri):
    """Open a File or a Web URL"""
    if uri.startswith('http://') or uri.startswith('https://'):
        return open_url(uri)
    else:
        return open_file(uri)


def open_url(url):
    """Return the games file data as an array"""
    try:
        with urllib.request.urlopen(url) as response:
            return response.read()
    except urllib.HTTPError as e:
        msg = "Could Not Open URL {}.\nThe Code is: {} "
        print(msg.format(url, e.code))
        sys.exit(1)
    except urllib.URLError as e:
        msg = "Could Not Open URL {}.\nThe Reason is: {} "
        print(msg.format(url.url, e.reason))
        sys.exit(1)


def open_file(uri):
    """Return the games file data as an array"""
    try:
        with open(uri, 'r') as f:
            return f.read()
    except IOError:
        msg = "Could not open file: `{}`"
        print(msg.format(uri))
        sys.exit(1)


def load_schedules(games_file):
    with open(games_file, 'r') as f:
        return [ScheduleItem.from_str(line) for line in f.readlines()]


def load_teams_data(data_file):
    with open(data_file, 'r') as csv_file:
        reader = csv.reader(csv_file)
        # Skip the header row
        next(reader)
        return [Team(row[0], row[2], row[3]) for row in reader]
