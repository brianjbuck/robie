from scheduleitem import Location, Result

__all__ = ('bubble_rank',)


def bubble_rank(teams):
    start_vals = {}
    end_vals = {}
    start_val = 75.0
    iterations = 10
    base = 25.0
    bonus = 1.4
    penalty = 0.6
    break_out = False
    t_iter_counter = 0
    equal = {}

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
    factor_home_win = low
    factor_home_loss = high
    factor_road_win = high
    factor_road_loss = low
    factor_neutral_win = mid
    factor_neutral_loss = mid
    total_score = 0.0
    total_games = 0

    # initialize starting values
    for team in teams.values():
        start_vals[team.name] = start_val
        equal[team.name] = False

    for x in range(iterations):
        for team in teams.values():
            curr_team = team
            schedule = team.schedule

            for game in schedule:

                t_iter_counter += 1
                opponent = game.opponent

                if opponent in teams:
                    opp_score = start_vals[opponent]

                    if game.result == Result.Win:
                        if game.location == Location.Home:
                            this_factor = factor_home_win
                        elif game.location == Location.Away:
                            this_factor = factor_road_win
                        else:
                            this_factor = factor_neutral_win
                        total_score += (opp_score + this_factor)
                    else:
                        if game.location == Location.Home:
                            this_factor = factor_home_loss
                        elif game.location == Location.Away:
                            this_factor = factor_road_loss
                        else:
                            this_factor = factor_neutral_loss
                        total_score += (opp_score - this_factor)
                # set the bonus/penalty for winning/losing to a DII/DIII team
                else:
                    if game.result == Result.Win:
                        # approx 50
                        total_score += (40.0 + factor_home_win)
                    elif game.result == Result.Loss:
                        #  equals 15 or in other words, bad news
                        total_score += (40.0 - factor_home_loss)
                total_games += 1

            end_vals[curr_team.name] = total_score / float(total_games)

            total_score = 0
            total_games = 0

            if round(start_vals[curr_team.name], 4) == round(end_vals[curr_team.name], 4):
                equal[curr_team.name] = True

                if False not in equal.values():
                    # pass
                    break_out = True

        start_vals = end_vals
        if break_out:
            break

    # convert the values before returning.
    for team, value in start_vals.items():
        teams[team].bubble_score = round(value / 100.0, 4)
        t = teams[team]
        print(t, t.bubble_score)
