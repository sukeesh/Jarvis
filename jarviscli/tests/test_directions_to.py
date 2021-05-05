import unittest
from mock import patch
from packages import directions_to, mapps


class TestDirectionsTo(unittest.TestCase):
    """
    A test class that contains test cases for the main method of
    directions_to.
    """

    @patch.object(mapps, 'directions')
    def test_directions_with_start_and_destination_city(self, mock_directions):
        from_city = 'London'
        to_city = 'Manchester'
        data = "from {} to {}".format(from_city, to_city)
        directions_to.main(data)
        mock_directions.assert_called_once_with(to_city, from_city)

    @patch.object(mapps, 'directions')
    def test_directions_with_destination_and_start_city(self, mock_directions):
        from_city = 'Madrid'
        to_city = 'Valencia'
        data = "to {} from {}".format(to_city, from_city)
        directions_to.main(data)
        mock_directions.assert_called_once_with(to_city, from_city)

    @patch.object(mapps, 'directions')
    def test_directions_with_only_destination_city(self, mock_directions):
        from_city = 0
        to_city = 'Paris'
        data = "to {}".format(to_city)
        directions_to.main(data)
        mock_directions.assert_called_once_with(to_city, from_city)


if __name__ == '__main__':
    unittest.main()
