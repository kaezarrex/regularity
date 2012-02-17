import unittest

from regularity import stats

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        pass

    def test_mean(self):
        self.assertEqual(stats.mean(1, 3), 2)
        self.assertEqual(stats.mean(0, 0, 0), 0)
        self.assertEqual(stats.mean(1), 1)
        self.assertEqual(stats.mean(1, 2), 1.5)
        self.assertEqual(stats.mean(-1, 2, 5), 2)

    def test_std(self):
        self.assertEqual(stats.std(1, 2, 1, 2), 0.5)

if __name__ == '__main__':
    unittest.main()
