import csv

from rankings import Bubble, RPI
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
    teams = load_teams_data('d1_2017.csv')
    schedule_items = load_schedules('GamesFiles/cbbga17.txt')

    for team in teams:
        team.load_schedule(schedule_items)

    rpi_ranker = RPI(teams)
    rpi_ranked = rpi_ranker.rank()
    bubble_ranker = Bubble(teams)
    bubble_ranked = bubble_ranker.rank()
    team_count = len(teams)
    for i in range(team_count):
        print('{:>3} {:05.4f} {} {} {:>3} {:05.4f} {} {}'.format(
            rpi_ranked[i].rank,
            rpi_ranked[i].score,
            rpi_ranked[i].record,
            rpi_ranked[i].name,
            bubble_ranked[i].rank,
            bubble_ranked[i].score,
            bubble_ranked[i].record,
            bubble_ranked[i].name
        )
    )

    # TODO: Make ranker callable class
    # TODO: Implement SOS
    # TODO: Make option to remove postseason games from output
