import unittest
import packages.movie as movie


class MovieTest(unittest.TestCase):

    def test_cast(self):
        d = movie.cast("Interstellar")
        self.assertEqual(d[0]['name'], "Ellen Burstyn")

    def test_director(self):
        d = movie.director("Interstellar")
        self.assertEqual(d[0]['name'], "Christopher Nolan")

    def test_producer(self):
        d = movie.producer("Interstellar")
        self.assertEqual(d[0]['name'], "Kaari Autry")

    def test_year(self):
        d = movie.year("Interstellar")
        self.assertEqual(str(d), "2014")


if __name__ == '__main__':
    unittest.main()
