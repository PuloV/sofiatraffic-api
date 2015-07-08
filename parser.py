import requests
import re
import time
from html.parser import HTMLParser
import json

class PageParsing:

    """Parsing class with static methods"""

    MAIN_PAGE = "http://schedules.sofiatraffic.bg/"
    TRANSPORT_RE = '(tramway|trolleybus|autobus){1}'
    a = 0

    @classmethod
    def parseScheduleButtons(cls, content):
        SCHEDULE_BTN_ID_RE = 'id="schedule_\d*_button"'
        schedule_btns = re.findall(SCHEDULE_BTN_ID_RE, content)

        # contains the found schedule ids
        btns = []

        for btn in schedule_btns:
            schedule_id = btn.replace('id="schedule_', "")
            schedule_id = schedule_id.replace('_button"', "")
            btns.append(schedule_id)
        return btns

    @classmethod
    def parseScheduleName(cls, content, schedule_id):
        SCHEDULE_BTN_RE = '<a.*?id="schedule_{}_button".*?</a>'.format(schedule_id)
        SCHEDULE_BTN_TITLE_RE = '<span>.*?</span>'
        schedule_btn = re.findall(SCHEDULE_BTN_RE, content)[-1]
        schedule_title = re.findall(SCHEDULE_BTN_TITLE_RE, schedule_btn).pop()
        return schedule_title

    @classmethod
    def parseRoutesStops(cls, content):
        STOPS_LI_RE = '<li class="\s+stop_\d*">.*?</li>'
        STOP_NAME_A_RE = '<a .*? class="stop_change".*?>.*?</a>'
        STOP_NAME_RE = '>.*?<'
        STOP_HREF_A_RE = '<a.*?class="stop_link".*?>.*?</a>'
        STOP_HREF_RE = 'id=".*?"'
        stops_li = re.findall(STOPS_LI_RE, content)

        # contains the found stops
        stops = []

        for stop_li in stops_li:
            # get the first (and only) stop name a tag
            stop_name_a = re.findall(STOP_NAME_A_RE, stop_li).pop()
            # get the first (and only) stop name from a tag
            stop_name = re.findall(STOP_NAME_RE, stop_name_a).pop()
            stop_name = stop_name.replace(">", "")
            stop_name = stop_name.replace("<", "")

            # get the first (and only) stop href a tag
            stop_href_a = re.findall(STOP_HREF_A_RE, stop_li).pop()
            # get the first (and only) stop href from a tag
            stop_href = re.findall(STOP_HREF_RE, stop_href_a).pop()
            stop_href = stop_href.replace('id="', "")
            stop_href = stop_href.replace('"', "")

            ids = re.findall("\d{1,}", stop_href)

            stops.append({
                "stop_name": stop_name,
                "schedule": "",
                "direction": "",
                "stop_no": ids[2]
                })

        return stops

    @classmethod
    def parseRoutesTimes(cls, content):
        TIME_RE = '\d{0,2}:\d{2}'
        time_resilts = re.findall(TIME_RE, content)
        return time_resilts
        hours = [time.strptime(hm, "%H:%M") for hm in time_resilts]
        return hours

    @classmethod
    def generateRouteStopsURL(cls, schedule, direction, stop_no):
        # "server/html/schedule_load/4018/1165/1254"
        return "server/html/schedule_load/{}/{}/{}".format(schedule, direction, stop_no)

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
        stops = cls.parseRoutesStops(content)
        schedules = cls.parseScheduleButtons(content)
        direction_stops_times = []

        for schedule in schedules:
            # get the schedule type name
            schedule_name = cls.parseScheduleName(content, schedule)

            for direction in directions:
                # get the direction id
                direction_id = re.findall("\d{1,}", direction[0]).pop()

                for stop in stops:
                    # set the direction and schedule
                    stop["schedule"] = schedule_name
                    stop["direction"] = direction[1]
                    # get the url for this stop
                    stop_url = cls.generateRouteStopsURL(schedule, direction_id, stop["stop_no"])
                    stop_url = "{}{}".format(cls.MAIN_PAGE, stop_url)
                    sr = requests.get(stop_url)
                    stop_content = "{}".format(sr.content)

                    # check for wrong request with empty body
                    if stop_content == "":
                        continue

                    # get all times for this route
                    schedule_times = cls.parseRoutesTimes(stop_content)

                    # check for wrong request with empty body
                    if len(schedule_times) == 0:
                        continue

                    direction_stops_times.append({
                        "stop": stop,
                        "url": stop_url,
                        "times": schedule_times,
                        "schedule_id": schedule,
                        "direction_id": direction_id
                        })
                    break

        print(json.dumps(direction_stops_times))


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
