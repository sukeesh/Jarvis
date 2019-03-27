import unittest
from mock import patch
from packages import near_me, mapps


class NearMeTest(unittest.TestCase):

    def setUp(self):
        self.things = 'charities'
        self.city = 'Valencia'

    @patch.object(mapps, 'search_near')
    def test_what_to_search_where_is_passed_to_mapps(self, mock_search_near):
        data = "{} | {}".format(self.things, self.city)
        near_me.main(data)
        mock_search_near.assert_called_once_with(self.things, self.city)


if __name__ == '__main__':
    unittest.main()
