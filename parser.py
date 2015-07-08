import requests
import re
import time
from html.parser import HTMLParser


class PageParsing:

    """Parsing class with static methods"""

    MAIN_PAGE = "http://schedules.sofiatraffic.bg/"
    TRANSPORT_RE = '(tramway|trolleybus|autobus){1}'
    a = 0

    @classmethod
    def parseRoutesTimes(cls, content):
        TIME_RE = '\d{0,2}:\d{2}'
        time_resilts = re.findall(TIME_RE, content)
        hours = [time.strptime(hm, "%H:%M") for hm in time_resilts]
        return hours


    @classmethod
    def getRouteDirectionsPage(cls, route):
        route_url = "{}{}".format(cls.MAIN_PAGE, route)
        r = requests.get(route_url)
        content = "{}".format(r.content)

        # collect data for the directions of the route
        DIRECTIONS_RE = '<a href="/{}#direction/\d*" id="schedule_direction_\d*_\d*_button" class=".*?schedule_view_direction_tab">.*?</a>'.format(route)
        directions_result = re.findall(DIRECTIONS_RE, content)
        directions = set()

        # parse the data of the directions
        for direction in directions_result:

            # get the route url
            URL_RE = '/\w*/.*?/\d*'
            url_result = re.search(URL_RE, direction)
            url = url_result.group(0)
            url = url.replace("/", "", 1)

            # get the route title
            TITLE_RE = 'n>.*?<'
            title_result = re.search(TITLE_RE, direction)
            title = title_result.group(0)
            title = title.replace("n>", "")
            title = title.replace("<", "")
            directions.add((url, title))

        # get all times for this route
        schedule_times = cls.parseRoutesTimes(content)

        # contain the filltered times pnly for the first stations
        start_station_times = {}
        prev_time = None
        dir_count = 0

        # filter the station times
        for tm in schedule_times:
            if prev_time and prev_time > tm:
                dir_count += 1

            try:
                direction = list(directions)[dir_count][0]
            except IndexError:
                break

            if start_station_times.get(direction, False) == False:
                start_station_times[direction] = []

            start_station_times.get(direction).append(tm)
            prev_time = tm

        print(start_station_times)

    @classmethod
    def parseMainPage(cls):
        r = requests.get(cls.MAIN_PAGE)

        content = "{}".format(r.content)

        class TransportLinksParser(HTMLParser):

            def __init__(self):
                HTMLParser.__init__(self)
                self.recording = 0
                self.data = []
                self.link = ""

            def handle_starttag(self, tag, attributes):

                if tag != 'a':
                    return

                for name, val in attributes:
                    if name == 'href' and re.match(cls.TRANSPORT_RE, val):
                        self.recording += 1
                        self.link = val
                        break
                    else:
                        self.link = ""

            def handle_endtag(self, tag):
                if tag == 'a' and self.recording:
                    self.recording -= 1

            def handle_data(self, data):
                if self.recording and self.link != "":
                    self.data.append({data: self.link})

        lp = TransportLinksParser()
        lp.feed(content)

        urls = lp.data
        for url in urls:
            line = list(url.keys())[0]
            cls.getRouteDirectionsPage(url.get(line))
            return


PageParsing.parseMainPage()
