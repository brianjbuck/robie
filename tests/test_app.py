import contextlib
import io
import json
import sys
import unittest

from robie.app import main


class TestTeam(unittest.TestCase):
    def setUp(self):
        while len(sys.argv) > 1:
            sys.argv.pop(-1)

    def tearDown(self):
        while len(sys.argv) > 1:
            sys.argv.pop(-1)

    def test_main_with_no_args(self):
        with self.assertRaises(SystemExit):
            main()

    def test_main_with_only_teams(self):
        sys.argv.append('-t')
        sys.argv.append('teams.txt')
        with self.assertRaises(SystemExit):
            main()

    def test_main_with_only_data_file(self):
        sys.argv.append('-u')
        sys.argv.append('data.txt')
        with self.assertRaises(SystemExit):
            main()

    def test_main_with_teams_and_data_file(self):
        args = [
            '-t', 'tests/teams.txt',
            '-u', 'tests/data.txt'
        ]
        for arg in args:
            sys.argv.append(arg)
        main()

    def test_main_with_method_bubble(self):
        args = [
            '-t', 'tests/teams.txt',
            '-u', 'tests/data.txt',
            '-m', 'bubble'
        ]
        for arg in args:
            sys.argv.append(arg)

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            main()
        expected_output = [
            '  1	0.5905	(9-1)	Team_C',
            '  2	0.5429	(7-3)	Team_B',
            '  3	0.5072	(6-4)	Team_A',
            '  4	0.4612	(6-6)	Team_D',
            '  5	0.3881	(2-8)	Team_E',
            '  6	0.3745	(3-9)	Team_F'
        ]
        actual_output = f.getvalue().split('\n')
        for v1, v2 in zip(expected_output, actual_output):
            self.assertEqual(v1, v2)

    def test_main_with_method_rpi(self):
        args = [
            '-t', 'tests/teams.txt',
            '-u', 'tests/data.txt',
            '-m', 'rpi'
        ]
        for arg in args:
            sys.argv.append(arg)

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            main()
        expected_output = [
            '  1	0.5797	(9-1)	Team_C',
            '  2	0.5464	(7-3)	Team_B',
            '  3	0.5297	(6-4)	Team_A',
            '  4	0.5133	(6-6)	Team_D',
            '  5	0.4769	(3-9)	Team_F',
            '  6	0.4630	(2-8)	Team_E'
        ]
        actual_output = f.getvalue().split('\n')
        for v1, v2 in zip(expected_output, actual_output):
            self.assertEqual(v1, v2)

    def test_main_with_method_rpiadj(self):
        args = [
            '-t', 'tests/teams.txt',
            '-u', 'tests/data.txt',
            '-m', 'rpiadj'
        ]
        for arg in args:
            sys.argv.append(arg)

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            main()

        expected_output = [
            '  1	0.5711	(9-1)	Team_C',
            '  2	0.5537	(7-3)	Team_B',
            '  3	0.5345	(6-4)	Team_A',
            '  4	0.5177	(6-6)	Team_D',
            '  5	0.4594	(3-9)	Team_F',
            '  6	0.4487	(2-8)	Team_E'
        ]
        actual_output = f.getvalue().split('\n')
        for v1, v2 in zip(expected_output, actual_output):
            self.assertEqual(v1, v2)

    def test_main_with_method_sos(self):
        args = [
            '-t', 'tests/teams.txt',
            '-u', 'tests/data.txt',
            '-m', 'sos'
        ]
        for arg in args:
            sys.argv.append(arg)

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            main()

        expected_output = [
            '  1	0.5525	(3-9)	Team_F',
            '  2	0.5506	(2-8)	Team_E',
            '  3	0.5178	(6-6)	Team_D',
            '  4	0.5063	(6-4)	Team_A',
            '  5	0.4952	(7-3)	Team_B',
            '  6	0.4730	(9-1)	Team_C'
        ]
        actual_output = f.getvalue().split('\n')
        for v1, v2 in zip(expected_output, actual_output):
            self.assertEqual(v1, v2)

    def test_main_with_unknown_method(self):
        args = [
            '-t', 'tests/teams.txt',
            '-u', 'tests/data.txt',
            '-m', 'asdf'
        ]
        for arg in args:
            sys.argv.append(arg)
        with self.assertRaises(SystemExit):
            main()

    def test_main_outputs_json(self):
        args = [
            '-t', 'tests/teams.txt',
            '-u', 'tests/data.txt',
            '-f', 'json'
        ]
        for arg in args:
            sys.argv.append(arg)

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            main()

        output = json.loads(f.getvalue())
        self.assertIsInstance(output, list)
        self.assertTrue(len(output) == 6)
