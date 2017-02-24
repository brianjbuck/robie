import csv
import json

import terminaltables

from rankings import do_bubble, do_rpi, do_sos, do_rpi_adjusted
from scheduleitem import ScheduleItem
from team import Team, TeamEncoder


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

    # rpi_ranked = do_rpi(teams)
    # sos_ranked = do_sos(teams)
    bubble_ranked = do_bubble(teams)

    print(
        json.dumps(bubble_ranked, cls=TeamEncoder, indent=2)
    )
    # rpi_adjusted_ranked = do_rpi_adjusted(teams)
    #
    # data = [[
    #     'Bubble Rank',
    #     'Score',
    #     'Team',
    #     'RPI Rank',
    #     'Score',
    #     'Team',
    #     'RPI Adjusted',
    #     'Score',
    #     'Team'
    # ]]

    # for i in range(len(teams)):
    #     bubble_team = bubble_ranked[i]
    #     rpi_team = rpi_ranked[i]
    #     rpi_adjusted_team = rpi_adjusted_ranked[i]
    #     data.append([
    #         '{:>3}'.format(bubble_team.rank),
    #         '{:05.4f}'.format(round(bubble_team.score, 4)),
    #         '({}) {}'.format(bubble_team.record, bubble_team.name),
    #         '{:>3}'.format(rpi_team.rank),
    #         '{:05.4f}'.format(round(rpi_team.score, 4)),
    #         '({}) {}'.format(rpi_team.record, rpi_team.name),
    #         '{:>3}'.format(rpi_adjusted_team.rank),
    #         '{:05.4f}'.format(round(rpi_adjusted_team.score, 4)),
    #         '({}) {}'.format(rpi_adjusted_team.record, rpi_adjusted_team.name),
    #     ])
    #
    # table = terminaltables.AsciiTable(data)
    # print(table.table)

    # TODO: Make option to remove postseason games from output
