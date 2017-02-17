from scheduleitem import Game, Location, Result


__all__ = ('Team',)


class Team:
    def __init__(self, name, mascot, conference):
        self.name = name
        self.mascot = mascot
        self.conference = conference
        self.record = '0-0'
        self.rank = 0
        self.bubble_score = 0.0
        self.rpi_rank = 0
        self.rpi = 0.0
        self.rpi_adj_rank = 0
        self.rpi_adj = 0.0
        self.sos_rank = 0
        self.sos = 0.0
        self.avg_opp_bubble_score = 0.0
        self.avg_opp_rank = 0
        self.avg_opp_rpi = 0
        self.avg_opp_rpi_rank = 0
        self.avg_opp_rpi_adj = 0
        self.avg_opp_rpi_adj_rank = 0
        self.avg_opp_sos = 0
        self.avg_opp_sos_rank = 0
        self.last_n_games = ''
        self.last_n_games_record = '0-0'
        self.schedule = []
        self.wins = 0
        self.losses = 0
        self.win_loss_str = ''
        self.wp = 0.0
        self.awp = 0.0
        self.owp = 0.0
        self.oowp = 0.0
        self.opponents = []

    def __str__(self):
        return '{} {}'.format(self.name, self.mascot)

    def __repr__(self):
        return '<{}: {} {}>'.format(
            self.__class__.__name__,
            self.name, self.mascot
        )

    @property
    def unique_opponents(self):
        return list(set(self.opponents))

    def create_schedule(self, schedule_items):
        """
        Take a list of ScheduleItem objects and load them into a team.
        Also, set the team's opponents at the same time.
        """
        for si in schedule_items:
            if self.name == si.home_team or self.name == si.away_team:
                if self.name == si.home_team:
                    location = Location.Home
                elif self.name == si.away_team:
                    location = Location.Away
                else:
                    location = Location.Neutral

                if location == Location.Home:
                    if si.home_team_score > si.away_team_score:
                        result = Result.Win
                    else:
                        result = Result.Loss
                elif location == Location.Away:
                    if si.home_team_score < si.away_team_score:
                        result = Result.Win
                    else:
                        result = Result.Loss
                elif location == Location.Neutral:
                    if self.name == si.home_team:
                        if si.home_team_score > si.away_team_score:
                            result = Result.Win
                        else:
                            result = Result.Loss
                    elif self.name == si.away_team:
                        if si.home_team_score < si.away_team_score:
                            result = Result.Win
                        else:
                            result = Result.Loss

                if self.name == si.home_team:
                    opponent = si.away_team
                else:
                    opponent = si.home_team

                game = Game(
                    game_date=si.game_date,
                    opponent=opponent,
                    score='',
                    location=location,
                    result=result
                )
                self.schedule.append(game)
                self.opponents.append(opponent)
