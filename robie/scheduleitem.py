import enum
from collections import namedtuple
from datetime import date


__all__ = ('Game', 'Location', 'Options', 'Result', 'ScheduleItem')


class Location(enum.Enum):
    Home = enum.auto()
    Away = enum.auto()
    Neutral = enum.auto()


class Result(enum.Enum):
    Win = enum.auto()
    Loss = enum.auto()


class Options(enum.Enum):
    OT1 = 1
    OT2 = 2
    OT3 = 3
    OT4 = 4
    OT5 = 5
    OT6 = 6
    Postseason = enum.auto()


Game = namedtuple(
    'Game',
    [
        'game_date',
        'opponent',
        'score',
        'location',
        'result',
        'city',
        'overtime',
        'postseason'
    ]
)


ScheduleItemBase = namedtuple(
    'ScheduleItem',
    [
        'game_date',
        'away_team',
        'away_team_score',
        'home_team',
        'home_team_score',
        'options',
        'location',
        'city',
        'home_team_result',
        'away_team_result'
    ]
)


class ScheduleItem(ScheduleItemBase):
    """
    Represents a single line in the Games File found at KenPom.com

    Example:
    11/13/2016 Florida Atlantic        68 SIU Edwardsville        77 N   Honolulu, HI
    """

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)

    @classmethod
    def date_from_string(cls, s):
        d = [int(val) for val in s.split('/')]
        return date(d[2], d[0], d[1])

    @classmethod
    def from_str(cls, in_str=''):
        away_team_score = int(in_str[34:38].strip())
        home_team_score = int(in_str[60:64].strip())

        if home_team_score > away_team_score:
            home_team_result = Result.Win
        else:
            home_team_result = Result.Loss

        if away_team_score > home_team_score:
            away_team_result = Result.Win
        else:
            away_team_result = Result.Loss

        options = in_str[64:69].strip()
        city = in_str[69:].strip()

        return ScheduleItem(
            game_date=cls.date_from_string(in_str[:11].strip()),
            away_team=in_str[11:34].strip(),
            away_team_score=away_team_score,
            home_team=in_str[38:60].strip(),
            home_team_score=home_team_score,
            options=options,
            location=Location.Neutral if options.casefold() == 'n' else '',
            city=city,
            home_team_result=home_team_result,
            away_team_result=away_team_result
        )

    @classmethod
    def from_list(cls, list_values):
        away_team_score = int(list_values[2])
        home_team_score = int(list_values[4])

        if home_team_score > away_team_score:
            home_team_result = Result.Win
        else:
            home_team_result = Result.Loss

        if away_team_score > home_team_score:
            away_team_result = Result.Win
        else:
            away_team_result = Result.Loss

        options = list_values[5].strip()
        city = list_values[6].strip()

        return ScheduleItem(
            game_date=cls.date_from_string(list_values[0].strip()),
            away_team=list_values[1].strip(),
            away_team_score=away_team_score,
            home_team=list_values[3].strip(),
            home_team_score=home_team_score,
            options=options,
            location=Location.Neutral if options.casefold() == 'n' else '',
            city=city,
            home_team_result=home_team_result,
            away_team_result=away_team_result
        )
