import unittest

from robie import rankings, filehandler


class TestRankings(unittest.TestCase):
    def setUp(self):
        self.teams = filehandler.load_teams(path='tests/teams.txt')
        schedule_items = filehandler.parse_schedules(uri='tests/data.txt')

        for team in self.teams:
            team.load_schedule(schedule_items)

    def tearDown(self):
        self.teams = []

    def test_bubble_ranking(self):
        expected_scores = {
            'Team_A': 0.5071547638798607,
            'Team_B': 0.5428690495941463,
            'Team_C': 0.5904880972131941,
            'Team_D': 0.46123471004048305,
            'Team_E': 0.3881071448322416,
            'Team_F': 0.374500016162932,
        }
        expected_ranks = {
            'Team_A': 3,
            'Team_B': 2,
            'Team_C': 1,
            'Team_D': 4,
            'Team_E': 5,
            'Team_F': 6
        }
        ranked_teams = rankings.do_bubble(self.teams)
        for team in ranked_teams:
            print(team, team.rank, team.score)
        for team in ranked_teams:
            self.assertEqual(team.score, expected_scores.get(team.name))
        for team in ranked_teams:
            self.assertEqual(team.rank, expected_ranks.get(team.name))

    def test_rpi_ranking(self):
        expected_scores = {
            'Team_A': 0.5296992481203008,
            'Team_B': 0.5463798384851016,
            'Team_C': 0.5797410192147034,
            'Team_D': 0.5133467278989667,
            'Team_E': 0.46297688666109715,
            'Team_F': 0.476894374282434,
        }
        expected_ranks = {
            'Team_A': 3,
            'Team_B': 2,
            'Team_C': 1,
            'Team_D': 4,
            'Team_E': 6,
            'Team_F': 5
        }
        ranked_teams = rankings.do_rpi(self.teams)
        for team in ranked_teams:
            print(team, team.score)
        for team in ranked_teams:
            self.assertEqual(team.score, expected_scores.get(team.name))
        for team in ranked_teams:
            self.assertEqual(team.rank, expected_ranks.get(team.name))

    def test_rpi_adjusted_ranking(self):
        expected_scores = {
            'Team_A': 0.5344611528822055,
            'Team_B': 0.5536715051517683,
            'Team_C': 0.5710871730608573,
            'Team_D': 0.517657072726553,
            'Team_E': 0.4486911723753829,
            'Team_F': 0.4593943742824339,
        }
        expected_ranks = {
            'Team_A': 3,
            'Team_B': 2,
            'Team_C': 1,
            'Team_D': 4,
            'Team_E': 6,
            'Team_F': 5
        }
        ranked_teams = rankings.do_rpi_adjusted(self.teams)
        for team in ranked_teams:
            print(team, team.score)
        for team in ranked_teams:
            self.assertEqual(team.score, expected_scores.get(team.name))
        for team in ranked_teams:
            self.assertEqual(team.rank, expected_ranks.get(team.name))

    def test_sos_ranking(self):
        expected_scores = {
            'Team_A': 0.506265664160401,
            'Team_B': 0.4951731179801355,
            'Team_C': 0.4729880256196045,
            'Team_D': 0.5177956371986223,
            'Team_E': 0.5506358488814629,
            'Team_F': 0.5525258323765786,
        }
        expected_ranks = {
            'Team_A': 4,
            'Team_B': 5,
            'Team_C': 6,
            'Team_D': 3,
            'Team_E': 2,
            'Team_F': 1
        }
        ranked_teams = rankings.do_sos(self.teams)
        for team in ranked_teams:
            print(team, team.score)
        for team in ranked_teams:
            self.assertEqual(team.score, expected_scores.get(team.name))
        for team in ranked_teams:
            self.assertEqual(team.rank, expected_ranks.get(team.name))
