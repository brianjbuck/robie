import copy

from scheduleitem import Location, Result

__all__ = (
    'Bubble', 'RPI', 'SOS',
    'do_bubble', 'do_sos',
    'do_rpi', 'do_rpi_adjusted'
)


class RankingBase:

    def __call__(self, *args, **kwargs):
        self.__init__(*args, **kwargs)
        return self.rank()

    def __init__(self, teams=None):
        # Work on a copy, not the original
        self.teams = copy.deepcopy(teams) if teams else []
        self.team_map = {team.name: team for team in self.teams} if teams else {}
        self.team_names = set(self.team_map.keys()) if teams else set()

    def rank(self):
        raise NotImplementedError

    def sort_and_rank(self):
        sorted_teams = sorted(self.teams, key=lambda t: t.score, reverse=True)
        for i, team in enumerate(sorted_teams, 1):
            team.rank = i
        return sorted_teams


class RPI(RankingBase):

    def rank(self):
        for team in self.teams:
            wp = team.wins / (team.wins + team.losses)
            owp = self.opponents_win_percentage(team.opponents)
            oowp = self.opponents_opponents_win_percentage(team.opponents)
            team.score = self.calculate(wp=wp, owp=owp, oowp=oowp)
        return self.sort_and_rank()

    @staticmethod
    def calculate(**kwargs):
        wp = kwargs.get('wp')
        owp = kwargs.get('owp')
        oowp = kwargs.get('oowp')
        return (0.25 * wp) + (0.5 * owp) + (0.25 * oowp)

    def opponents_win_percentage(self, opponents):
        wins = 0
        losses = 0
        for team_name in opponents:
            team = self.team_map.get(team_name)
            if team:
                wins += team.wins
                losses += team.losses
            else:
                continue
        return wins / (wins + losses)

    def opponents_opponents_win_percentage(self, opponents):
        opponents_opponents = []
        for opponent_name in opponents:
            opponent = self.team_map.get(opponent_name)
            if opponent:
                for opponents_opponent_name in opponent.opponents:
                    opponents_opponent = self.team_map.get(opponents_opponent_name)
                    if opponents_opponent:
                        opponents_opponents.append(opponents_opponent)
        wins = sum([team.wins for team in opponents_opponents])
        losses = sum([team.losses for team in opponents_opponents])
        return wins / (wins + losses)


class SOS(RPI):

    def rank(self):
        for team in self.teams:
            owp = self.opponents_win_percentage(team.opponents)
            oowp = self.opponents_opponents_win_percentage(team.opponents)
            team.score = self.calculate(owp=owp, oowp=oowp)
        return self.sort_and_rank()

    @staticmethod
    def calculate(**kwargs):
        owp = kwargs.get('owp')
        oowp = kwargs.get('oowp')
        return ((2.0 / 3.0) * owp) + ((1.0 / 3.0) * oowp)


class RPIAdjusted(RPI):

    def rank(self):
        for team in self.teams:
            wp = self.adjusted_win_percentage(team.schedule)
            owp = self.opponents_win_percentage(team.opponents)
            oowp = self.opponents_opponents_win_percentage(team.opponents)
            team.score = self.calculate(wp=wp, owp=owp, oowp=oowp)
        return self.sort_and_rank()

    @staticmethod
    def adjusted_win_percentage(schedule):
        home_win_count = 0
        road_win_count = 0
        neutral_win_count = 0
        home_loss_count = 0
        road_loss_count = 0
        neutral_loss_count = 0

        for game in schedule:
            if game.result == Result.Win:
                if game.location == Location.Home:
                    home_win_count += 1
                elif game.location == Location.Away:
                    road_win_count += 1
                else:
                    neutral_win_count += 1
            elif game.result == Result.Loss:
                if game.location == Location.Home:
                    home_loss_count += 1
                elif game.location == Location.Away:
                    road_loss_count += 1
                else:
                    neutral_loss_count += 1

        # Adjusted Win Count
        adjusted_win_count = (home_win_count * 0.6) + \
                             (neutral_win_count) + \
                             (road_win_count * 1.4)
        # Adjusted Loss Count
        adjusted_loss_count = (home_loss_count * 1.4) + \
                              (neutral_loss_count) + \
                              (road_loss_count * 0.6)
        # Adjusted Win Percentage
        return adjusted_win_count / (adjusted_win_count + adjusted_loss_count) if adjusted_win_count + adjusted_loss_count > 0 else 0.0


class Bubble(RankingBase):
    """
    start = 75.0
    base = 25.0
    high = base  # 25.0
    mid = base / bonus  # 17.85
    low = (base / bonus) * penalty  # 10.71
    """

    def __init__(self, teams=None, start=75.0, base=25.0, bonus=1.4, penalty=0.6):
        super().__init__(teams)

        self.starting_scores = {}
        self.ending_scores = {}
        self.iterations = 100
        self.start = start
        self.base = base
        self.bonus = bonus
        self.penalty = penalty
        self.break_out = False
        self.equal = {}

        high = base
        mid = base / bonus
        low = (base / bonus) * penalty

        # bonuses/penalties for winning/losing at home/road/neutral sites
        # it is assumed that home wins are easier to get than road wins
        # so the least points are awarded for winning at home while the
        # most points are awarded for winning on the road. The opposite is
        # true regarding losses. A team is penalized the most points for
        # losing at home while penalized the fewest for losing on the road.
        # Neutral wins/losses are in between home/road wins/losses amounts.
        self.factor_home_win = low
        self.factor_home_loss = -high
        self.factor_road_win = high
        self.factor_road_loss = -low
        self.factor_neutral_win = mid
        self.factor_neutral_loss = -mid

    def rank(self):
        """
        A team's score is equal to the value of the sum of each of it's
        opponent's score, plus or minus a bonus for winning or a penalty
        for losing against that opponent, divided by the number of games played.
        Example:
            Assume everyone starts with a score of 75.
            TeamA plays a schedule of {TeamB: Win, TeamC: Loss, TeamD: Win}

            sum([
                100, # TeamB, (75 + 25 bonus) for a win
                 50, # TeamC, (75 - 25 penalty) for loss
                100, # TeamD, (75 + 25 bonus) for a win
            ]) / 3
            ------
            83.33    # TeamA's score

            Repeat for TeamB, TeamC, TeamD

            Then do it again using the new scores in place of the starting
            score of 75 that we set for each team at the beginning.

            Eventually the scores will stabilize. Keep running the process
            until each team gets the same score for two successive cycles.
        """

        # initialize starting values
        for team in self.teams:
            self.starting_scores[team.name] = self.start
            self.equal[team.name] = False

        while not self.break_out:
            for team in self.teams:
                self.ending_scores[team.name] = self.calculate_ranking_for_team(team)

                starting_score = round(self.starting_scores[team.name], 4)
                ending_score = round(self.ending_scores[team.name], 4)
                if starting_score == ending_score:
                    self.equal[team.name] = True

                    if False not in self.equal.values():
                        self.break_out = True
            self.starting_scores = {k: v for k, v in self.ending_scores.items()}
            self.ending_scores = {}

        # convert the values before returning.
        for team in self.teams:
            team.score = self.starting_scores[team.name] / 100.0
        return self.sort_and_rank()

    def calculate_ranking_for_team(self, team):
        score = 0
        for game in team.schedule:
            opponent = game.opponent
            if opponent in self.team_names:  # D-I Team
                score += self.get_d1_opponent_score(game)
            else:  # D-II/D-III team
                score += self.get_d2_opponent_score(game)
        return score / float(len(team.schedule))

    def get_d1_opponent_score(self, game):
        opponent_score = self.starting_scores[game.opponent]
        if game.result == Result.Win:
            if game.location == Location.Home:
                factor = self.factor_home_win
            elif game.location == Location.Away:
                factor = self.factor_road_win
            else:
                factor = self.factor_neutral_win
        else:
            if game.location == Location.Home:
                factor = self.factor_home_loss
            elif game.location == Location.Away:
                factor = self.factor_road_loss
            else:
                factor = self.factor_neutral_loss
        return opponent_score + factor

    def get_d2_opponent_score(self, game):
        """
        Returns the value score for winning or losing a game against
        either a Division II or Division III school.
        """
        # Since a school in this scenario isn't in the list of teams
        # and we cannot know what their score is, arbitrarily set the
        # score to 40. Applying the bonus sets it to about 50 while
        # applying the penalty sets it to about 15. In other words,
        # we want to punish schools for playing weak schedules.
        if game.result == Result.Win:
            return 40.0 + self.factor_home_win
        else:
            return 40.0 + self.factor_home_loss


do_rpi = RPI()
do_rpi_adjusted = RPIAdjusted()
do_sos = SOS()
do_bubble = Bubble()
