import copy

from scheduleitem import Location, Result

__all__ = ('Bubble', 'RPI')


class RankingBase:

    def __init__(self, teams):
        self.teams = copy.deepcopy(teams)  # Work on a copy, not the original
        self.team_map = {team.name: team for team in self.teams}
        self.team_names = set(self.team_map.keys())

    def sort_and_rank(self):
        sorted_teams = sorted(self.teams, key=lambda t: t.score, reverse=True)
        for i, team in enumerate(sorted_teams, 1):
            team.rank = i
        return sorted_teams


class RPI(RankingBase):

    def rank(self):
        for team in self.teams:
            wp = team.wins / (team.wins + team.losses)

            opp_wins = 0
            opp_losses = 0
            for opponent_name in team.opponents:
                opponent = self.team_map.get(opponent_name)
                if opponent:
                    opp_wins += opponent.wins
                    opp_losses += opponent.losses
                else:
                    continue

                oopp_wins = 0
                oopp_losses = 0
                for opponents_opponents_name in opponent.opponents:
                    opponents_opponent = self.team_map.get(opponents_opponents_name)
                    if opponents_opponent:
                        oopp_wins += opponents_opponent.wins
                        oopp_losses += opponents_opponent.losses
                oowp = oopp_wins / (oopp_wins + oopp_losses)
            owp = opp_wins / (opp_wins + opp_losses)
            team.score = self.calculate_rpi(wp, owp, oowp)
        return self.sort_and_rank()

    @staticmethod
    def calculate_rpi(wp, owp, oowp):
        return (0.25 * wp) + (0.5 * owp) + (0.25 * oowp)

class SOS(RankingBase):

    def rank(self):
        pass


class Bubble(RankingBase):
    """
    start = 75.0
    base = 25.0
    high = base  # 25.0
    mid = base / bonus  # 17.85
    low = (base / bonus) * penalty  # 10.71
    """

    def __init__(self, teams, start=75.0, base=25.0, bonus=1.4, penalty=0.6):
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
            team.score = round(self.starting_scores[team.name] / 100.0, 4)
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
