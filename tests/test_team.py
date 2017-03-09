import json
import unittest

from robie import filehandler, rankings, team


class TestTeam(unittest.TestCase):
    def setUp(self):
        self.teams = filehandler.load_teams(path='tests/teams.txt')
        schedule_items = filehandler.load_schedules(uri='tests/data.txt')

        for team in self.teams:
            team.load_schedule(schedule_items)

        self.ranked = rankings.do_bubble(self.teams)

    def tearDown(self):
        self.teams = []
        self.ranked = []

    def test_json_encoder_serializes(self):
        data = json.loads(json.dumps(self.ranked, cls=team.TeamEncoder))
        self.assertTrue(len(data) > 0, 'No teams found. Did they fail to load?')

        team_dict = data[0]
        schedule_data = team_dict.get('schedule')
        self.assertTrue(len(schedule_data) > 0)

        keys = [
            'game_date', 'opponent', 'score', 'location',
            'result', 'city', 'overtime', 'postseason'
        ]
        game_data = schedule_data[0]
        for key in keys:
            self.assertTrue(key in game_data, 'Key: {} not found!'.format(key))
