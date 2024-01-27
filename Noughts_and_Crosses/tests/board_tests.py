import unittest
import sys
import os

from Noughts_and_Crosses.src import board


class PositionTestCase(unittest.TestCase):
    def test_test_test(self):
        self.assertTrue(1 == 1)

    def test_state(self):
        for case in [
            {'grid': [0, 0, 0, 0, 0, 0, 0, 0, 0], 'state': 'ongoing'},
            {'grid': [1, 2, 0, 1, 2, 0, 1, 0, 0], 'state': 'won'},
            {'grid': [1, 2, 1, 1, 2, 0, 0, 2, 0], 'state': 'won'},
            {'grid': [1, 1, 0, 0, 0, 0, 0, 0, 0], 'state': 'invalid'},
            {'grid': [2, 0, 0, 0, 0, 0, 0, 0, 0], 'state': 'invalid'},
            {'grid': [1, 1, 1, 0, 0, 0, 2, 2, 2], 'state': 'invalid'},
            {'grid': [1, 0, 0, 0, 1, 0, 0, 0, 1], 'state': 'invalid'},
            {'grid': [1, 2, 1, 2, 2, 1, 1, 1, 2], 'state': 'drawn'},
            {'grid': [1, 2, 1, 2, 2, 1, 1, 0, 2], 'state': 'ongoing'},
            {'grid': [1, 2, 1, 2, 2, 1, 1, 0, 0], 'state': 'ongoing'}
        ]:
            with self.subTest(case=case):
                target = board.Position(board.idifier(case['grid']), set())
                result = target.state()
                self.assertTrue(result == case['state'])

