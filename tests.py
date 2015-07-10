import unittest
from st_parser import *


def get_page(page):
    f = open(page, 'r')
    content = f.read()
    f.close()
    return content


class TestFetchingTraffic(unittest.TestCase):

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

if __name__ == '__main__':
    unittest.main()
