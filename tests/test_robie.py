import unittest

from . import context

from robie import rankings, filehandler


class CliTest(unittest.TestCase):
    def setUp(self):
        self.teams = filehandler.load_teams(path='tests/teams.txt')
        schedule_items = filehandler.load_schedules(uri='tests/data.txt')

        for team in self.teams:
            team.load_schedule(schedule_items)

    def tearDown(self):
        self.teams = []

    def test_bubble_ranking(self):
        expected_scores = {
            'Team_A': 0.5041787018237359,
            'Team_B': 0.5339406065856407,
            'Team_C': 0.5875120351570693,
            'Team_D': 0.458683799862728,
            'Team_E': 0.3851310827761169,
            'Team_F': 0.37705114680150353,
        }
        for team in rankings.do_bubble(self.teams):
            print(team, team.score)
        for team in rankings.do_bubble(self.teams):
            self.assertEqual(team.score, expected_scores.get(team.name))

    def test_rpi_ranking(self):
        expected_scores = {
            'Team_A': 0.5296992481203008,
            'Team_B': 0.5463798384851016,
            'Team_C': 0.5797410192147034,
            'Team_D': 0.5133467278989667,
            'Team_E': 0.46297688666109715,
            'Team_F': 0.476894374282434,
        }
        for team in rankings.do_rpi(self.teams):
            print(team, team.score)
        for team in rankings.do_rpi(self.teams):
            self.assertEqual(team.score, expected_scores.get(team.name))

    def test_rpi_adjusted_ranking(self):
        expected_scores = {
            'Team_A': 0.5344611528822055,
            'Team_B': 0.5507276645720581,
            'Team_C': 0.5710871730608573,
            'Team_D': 0.517657072726553,
            'Team_E': 0.4486911723753829,
            'Team_F': 0.461269374282434,
        }
        for team in rankings.do_rpi_adjusted(self.teams):
            print(team, team.score)
        for team in rankings.do_rpi_adjusted(self.teams):
            self.assertEqual(team.score, expected_scores.get(team.name))

    def test_sos_ranking(self):
        expected_scores = {
            'Team_A': 0.506265664160401,
            'Team_B': 0.4951731179801355,
            'Team_C': 0.4729880256196045,
            'Team_D': 0.5177956371986223,
            'Team_E': 0.5506358488814629,
            'Team_F': 0.5525258323765786,
        }
        for team in rankings.do_sos(self.teams):
            print(team, team.score)
        for team in rankings.do_sos(self.teams):
            self.assertEqual(team.score, expected_scores.get(team.name))