import argparse
import json

from filehandler import load_schedules, load_teams_data
from rankings import do_bubble, do_rpi, do_rpi_adjusted, do_sos
from team import TeamEncoder


parser = argparse.ArgumentParser(prog='Robie')
parser.add_argument(
    'uri',
    help='The file location to retrieve game data.'
)
parser.add_argument(
    '-s',
    '--store',
    action="store_true",
    default=False,
    help='Include this flag if you want to save the games file.'
)
parser.add_argument(
    '-m',
    '--method',
    default='bubble',
    choices=['bubble', 'rpi', 'rpiadj', 'sos'],
    help='The method to use.'
)
parser.add_argument(
    '-f',
    '--format',
    default='plain',
    choices=['plain', 'json'],
    help='The output format to print.'
)
parser.add_argument(
    '-p',
    '--postseason',
    action="store_true",
    default=False,
    help='Include this flag if you want to include postseason games.'
)

if __name__ == '__main__':
    args = parser.parse_args()
    teams = load_teams_data('d1_2017.csv')
    schedule_items = load_schedules(uri=args.uri, store_file=args.store)

    for team in teams:
        team.load_schedule(schedule_items, include_postseason=args.postseason)

    if args.method.lower() == 'bubble':
        ranked = do_bubble(teams)
    elif args.method.lower() == 'rpi':
        ranked = do_rpi(teams)
    elif args.method.lower() == 'rpiadj':
        ranked = do_rpi_adjusted(teams)
    elif args.method.lower() == 'sos':
        ranked = do_sos(teams)
    else:
        msg = 'Specified method not recognized: `{}`'
        raise RuntimeError(msg.format(args.method))

    if args.format.lower() == 'plain':
        output = '{:>3}\t{:05.4f}\t({})\t{}'
        for ranked_team in ranked:
            print(
                output.format(
                    ranked_team.rank,
                    ranked_team.score,
                    ranked_team.record,
                    ranked_team.name
                )
            )
    elif args.format.lower() == 'json':
        print(json.dumps(ranked, cls=TeamEncoder, indent=2))
    else:
        msg = 'Specified output format not recognized: `{}`'
        raise RuntimeError(msg.format(args.format))
