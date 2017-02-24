import datetime
import json

from scheduleitem import Game, Location, Result


__all__ = ('Team',)


class Team:
    def __init__(self, name, mascot, conference):
        self.name = name
        self.mascot = mascot
        self.conference = conference
        self.rank = 0
        self.score = 0.0
        self.opponents = []
        self.schedule = []
        self.wins = 0
        self.losses = 0
        self.last_n_games = ''
        self.last_n_games_record = '0-0'
        self.win_loss_str = ''

    def __str__(self):
        return '{} {}'.format(self.name, self.mascot)

    def __repr__(self):
        return '<{}: {} {}>'.format(
            self.__class__.__name__,
            self.name, self.mascot
        )

    @property
    def serializable_fields(self):
        return (
            'name',
            'mascot',
            'conference',
            'rank',
            'score',
            'opponents',
            'schedule',
            'wins',
            'losses'
        )

    @property
    def record(self):
        return '{}-{}'.format(self.wins, self.losses)

    @property
    def unique_opponents(self):
        return list(set(self.opponents))

    def load_schedule(self, schedule_items):
        """
        Take a list of ScheduleItem objects and load them into a team.
        Also, set the team's opponents at the same time.
        """
        for schedule_item in schedule_items:
            home_team_name = schedule_item.home_team
            away_team_name = schedule_item.away_team
            if self.name == home_team_name or self.name == away_team_name:
                location = self.get_game_location(schedule_item)
                result = self.get_game_result(location, schedule_item)
                opponent = self.get_game_opponent(schedule_item)
                score = self.get_game_score(schedule_item)

                game = Game(
                    game_date=schedule_item.game_date,
                    opponent=opponent,
                    score=score,
                    location=location,
                    result=result
                )
                self.schedule.append(game)
                self.opponents.append(opponent)
        self.wins = len([g for g in self.schedule if g.result == Result.Win])
        self.losses = len([g for g in self.schedule if g.result == Result.Loss])

    def get_game_score(self, schedule_item):
        home_team_score = schedule_item.home_team_score
        away_team_score = schedule_item.away_team_score

        if self.name == schedule_item.home_team:
            return '{} - {}'.format(home_team_score, away_team_score)
        else:
            return '{} - {}'.format(away_team_score, home_team_score)

    def get_game_opponent(self, schedule_item):
        if self.name == schedule_item.home_team:
            opponent = schedule_item.away_team
        else:
            opponent = schedule_item.home_team
        return opponent

    def get_game_location(self, schedule_item):
        home_team_name = schedule_item.home_team
        away_team_name = schedule_item.away_team
        is_neutral_site = 'n' in schedule_item.options.casefold()
        if self.name == home_team_name and not is_neutral_site:
            location = Location.Home
        elif self.name == away_team_name and not is_neutral_site:
            location = Location.Away
        else:
            location = Location.Neutral
        return location

    def get_game_result(self, location, schedule_item):
        result = None
        home_team_score = schedule_item.home_team_score
        away_team_score = schedule_item.away_team_score
        if location == Location.Home:
            if home_team_score > away_team_score:
                result = Result.Win
            else:
                result = Result.Loss
        elif location == Location.Away:
            if home_team_score < away_team_score:
                result = Result.Win
            else:
                result = Result.Loss
        elif location == Location.Neutral:
            if self.name == schedule_item.home_team:
                if home_team_score > away_team_score:
                    result = Result.Win
                else:
                    result = Result.Loss
            elif self.name == schedule_item.away_team:
                if home_team_score < away_team_score:
                    result = Result.Win
                else:
                    result = Result.Loss
        return result


# For serialization of the `Team` object
class TeamEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Team):
            # Only serialize the specified fields
            if obj.serializable_fields:
                obj_map = {
                    k: v for k, v in obj.__dict__.items()
                    if k in obj.serializable_fields
                }
            else:
                obj_map = obj.__dict__
            # Game objects don't serialize correctly so find them and
            # convert them to `OrderedDict` objects here which do
            # serialize correctly. Accessing the `_asdict()` method is the
            # official way of doing this.
            obj_map['schedule'] = [g._asdict() for g in obj_map.get('schedule')]
            return obj_map
        elif isinstance(obj, Location):
            return obj.name
        elif isinstance(obj, Result):
            return obj.name
        elif isinstance(obj, datetime.date):
            return str(obj)
        return json.JSONEncoder.default(self, obj)
