import requests
import re
from html.parser import HTMLParser


class PageParsing:

    """Parsing class with static methods"""

    MAIN_PAGE = "http://schedules.sofiatraffic.bg/"
    TRANSPORT_RE = '(tramway|trolleybus|autobus){1}'

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
                        print(tag, name, val)
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
        print(lp.data)


PageParsing.parseMainPage()
