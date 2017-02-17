import csv

from bubblerank import bubble_rank
from scheduleitem import ScheduleItem
from team import Team


def load_schedules(games_file):
    with open(games_file, 'r') as f:
        return [ScheduleItem.from_str(line) for line in f.readlines()]


def load_teams_data(data_file):
    with open(data_file, 'r') as csv_file:
        reader = csv.reader(csv_file)
        # Skip the header row
        next(reader)
        return [Team(row[0], row[2], row[3]) for row in reader]


if __name__ == '__main__':
    teams_list = load_teams_data('d1_2017.csv')
    schedule_items = load_schedules('GamesFiles/cbbga17.txt')

    teams = {}
    for team in teams_list:
        team.create_schedule(schedule_items)
        teams[team.name] = team
    bubble_rank(teams)
