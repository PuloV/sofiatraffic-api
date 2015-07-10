import unittest
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


class TestParseRouteStations(unittest.TestCase):

    """ Class testing the parse_routes_stops function """

    def test_fetching_bus_stops(self):
        page = get_page("./test_files/bus_stops.html")
        stops = PageParsing.parse_routes_stops(page)
        self.assertEqual(len(stops), 20)


class TestParseScheduleName(unittest.TestCase):

    """ Class testing the parse_schedule_name function """

    def test_fetching_1_schedule_name(self):
        page = get_page("./test_files/1_schedule_name.html")
        schedule = PageParsing.parse_schedule_name(page, 123)
        self.assertEqual(schedule, "Daily")

    def test_fetching_2_schedule_name(self):
        page = get_page("./test_files/2_schedule_name.html")
        schedule = PageParsing.parse_schedule_name(page, 123)
        self.assertEqual(schedule, "Weekend")

    def test_fetching_1_schedule_button(self):
        page = get_page("./test_files/1_schedule_name.html")
        schedule_btns = PageParsing.parse_schedule_buttons(page)
        self.assertEqual(len(schedule_btns), 1)

    def test_fetching_2_schedule_button(self):
        page = get_page("./test_files/2_schedule_name.html")
        schedule_btns = PageParsing.parse_schedule_buttons(page)
        self.assertEqual(len(schedule_btns), 2)

    def test_fetching_check_is_weekly_scheduleFalse(self):
        self.assertFalse(PageParsing.check_is_weekly_schedule("wrong_string"))

    def test_fetching_check_is_weekly_scheduleTrue(self):
        self.assertTrue(PageParsing.check_is_weekly_schedule(b'\xd0\xb4\xd0\xb5\xd0\xbb\xd0\xbd\xd0\xb8\xd0\xba'))


class TestParseRoute(unittest.TestCase):

    """ Class testing the generate_route_stops_url && parse_routes_stops function """

    def test_generate_route_stops_url(self):
        url = PageParsing.generate_route_stops_url(1, 2, 3)
        self.assertEqual(url, "server/html/schedule_load/1/2/3")

    def test_fetching_routes_times(self):
        page = get_page("./test_files/2_times.html")
        times = PageParsing.parse_routes_times(page)
        self.assertEqual(len(times), 2)


if __name__ == '__main__':
    unittest.main()
