import unittest
from mock import patch
from packages import near_me, mapps


class TestNearMe(unittest.TestCase):
    """
    A test class that contains test cases for the main method of
    near_me.
    """

    @patch.object(mapps, 'search_near')
    def test_near_with_things_and_specific_city(self, mock_search_near):
        things = 'charities'
        city = 'Valencia'
        data = "{} | {}".format(things, city)
        near_me.main(data)
        mock_search_near.assert_called_once_with(things, city)

    @patch.object(mapps, 'search_near')
    def test_near_with_things_and_my_location(self, mock_search_near):
        things = 'restaurants'
        city = 'me'
        expected_city = 0
        data = "{} | {}".format(things, city)
        near_me.main(data)
        mock_search_near.assert_called_once_with(things, expected_city)

    @patch.object(mapps, 'search_near')
    def test_near_with_things_and_empty_space(self, mock_search_near):
        things = 'bars'
        city = ''
        data = "{} | {}".format(things, city)
        near_me.main(data)
        mock_search_near.assert_called_once_with(things, city)


if __name__ == '__main__':
    unittest.main()
