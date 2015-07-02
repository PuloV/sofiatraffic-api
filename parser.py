import requests
import re
from html.parser import HTMLParser


class PageParsing:

    """Parsing class with static methods"""

    MAIN_PAGE = "http://schedules.sofiatraffic.bg/"
    TRANSPORT_RE = '(tramway|trolleybus|autobus){1}'

    @classmethod
    def getRouteDirectionsPage(cls, route):
        route_url = "{}{}".format(cls.MAIN_PAGE, route)
        r = requests.get(route_url)
        content = "{}".format(r.content)
        DIRECTIONS_RE = '<a href="/{}#direction/\d*" id="schedule_direction_\d*_\d*_button" class=".*?schedule_view_direction_tab">.*?</a>'.format(route)

        directions_result = re.findall(DIRECTIONS_RE, content)
        directions = set()
        for direction in directions_result:
            URL_RE = '/\w*/.*?/\d*'
            url_result = re.search(URL_RE, direction)
            url = url_result.group(0)
            TITLE_RE = 'n>.*?<'
            title_result = re.search(TITLE_RE, direction)
            title = title_result.group(0)
            directions.add((url, title))

        for direction in directions:
            print( direction[0])



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
