import unittest
import codecs
from st_parser import *


def get_page(page):
    f = open(page, 'r')
    content = f.read()
    f.close()
    return content


class TestParseTrafficLinks(unittest.TestCase):

    """ Class testing the parse_traffic_links function """

    def test_fetching_buses(self):
        page = get_page("./test_files/buses.html")
        traffic = PageParsing.parse_traffic_links(page)
        self.assertEqual(len(traffic), 50)

    def test_fetching_tramway(self):
        page = get_page("./test_files/tramway.html")
        traffic = PageParsing.parse_traffic_links(page)
        self.assertEqual(len(traffic), 15)

    def test_fetching_trolleybus(self):
        page = get_page("./test_files/trolleybus.html")
        traffic = PageParsing.parse_traffic_links(page)
        self.assertEqual(len(traffic), 10)

    def test_fetching_no_transport(self):
        page = get_page("./test_files/no_transport.html")
        traffic = PageParsing.parse_traffic_links(page)
        self.assertEqual(len(traffic), 0)


class TestParseRouteDirection(unittest.TestCase):

    """ Class testing the parse_route_direction function """

    def test_fetching_2_directions(self):
        page = get_page("./test_files/2_directions.html")
        directions = PageParsing.parse_route_direction(page, "tramway/1")
        self.assertEqual(len(directions), 2)

    def test_fetching_wrong_directions(self):
        page = get_page("./test_files/4_directions.html")
        directions = PageParsing.parse_route_direction(page, "tramway/1")
        self.assertEqual(len(directions), 0)

    def test_fetching_4_directions(self):
        page = get_page("./test_files/4_directions.html")
        directions = PageParsing.parse_route_direction(page, "autobus/69")
        self.assertEqual(len(directions), 4)


if __name__ == '__main__':
    unittest.main()
