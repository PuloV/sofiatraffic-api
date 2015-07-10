import requests
import re
import time
from html.parser import HTMLParser
import json
import os
import datetime
import time
import threading
from multiprocessing.dummy import Pool as ThreadPool


class PageParsing:

    """Parsing class with static methods"""

    MAIN_PAGE = "http://schedules.sofiatraffic.bg/"
    TRANSPORT_RE = '(tramway|trolleybus|autobus){1}'
    a = 0

    @classmethod
    def parse_schedule_buttons(cls, content):
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
    def parse_schedule_name(cls, content, schedule_id):
        SCHEDULE_BTN_RE = 'id="schedule_{}_button".*?>.*?</a>'.format(schedule_id)
        SCHEDULE_BTN_TITLE_RE = '<span>.*?</span>'
        schedule_btn = re.findall(SCHEDULE_BTN_RE, content)[-1]
        schedule_title = re.findall(SCHEDULE_BTN_TITLE_RE, schedule_btn)[-1]
        schedule_title = schedule_title.replace("<span>", "")
        schedule_title = schedule_title.replace("</span>", "")
        return schedule_title

    @classmethod
    def check_is_weekly_schedule(cls, schedule):
        # no idea why this doesnt work
        # return schedule == "делник"
        return schedule == b'\xd0\xb4\xd0\xb5\xd0\xbb\xd0\xbd\xd0\xb8\xd0\xba'

    @classmethod
    def parse_routes_stops(cls, content):
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
    def parse_routes_times(cls, content):
        TIME_RE = '\d{0,2}:\d{2}'
        time_resilts = re.findall(TIME_RE, content)
        return time_resilts
        hours = [time.strptime(hm, "%H:%M") for hm in time_resilts]
        return hours

    @classmethod
    def generate_route_stops_url(cls, schedule, direction, stop_no):
        # "server/html/schedule_load/4018/1165/1254"
        return "server/html/schedule_load/{}/{}/{}".format(schedule, direction, stop_no)

    @classmethod
    def get_route_directions_page(cls, route):
        time_last = time.time()
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
        stops = cls.parse_routes_stops(content)
        schedules = cls.parse_schedule_buttons(content)
        direction_stops_times = []

        for schedule in schedules:
            # get the schedule type name
            schedule_name = cls.parse_schedule_name(content, schedule)

            for direction in directions:
                # get the direction id
                direction_id = re.findall("\d{1,}", direction[0]).pop()

                for stop in stops:
                    # set the direction and schedule
                    stop["schedule"] = schedule_name
                    stop["direction"] = direction[1]
                    # get the url for this stop
                    stop_url = cls.generate_route_stops_url(schedule, direction_id, stop["stop_no"])
                    stop_url = "{}{}".format(cls.MAIN_PAGE, stop_url)
                    sr = requests.get(stop_url)
                    stop_content = "{}".format(sr.content)

                    # check for wrong request with empty body
                    if stop_content == "":
                        continue

                    # get all times for this route
                    schedule_times = cls.parse_routes_times(stop_content)

                    # check for wrong request with empty body
                    if len(schedule_times) == 0:
                        continue

                    direction_stops_times.append({
                        "url": stop_url,
                        "times": schedule_times,
                        "schedule_id": schedule,
                        "weekly_schedule": cls.check_is_weekly_schedule(schedule_name),
                        "direction_id": direction_id,
                        "stop": {
                            "schedule": schedule_name,
                            "direction": direction[1],
                            "stop_name": stop["stop_name"],
                            "stop_no": stop["stop_no"]
                            }
                        })

        # print(json.dumps(direction_stops_times))
        today = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
        json_file = "{}/{}.json".format(today, route.replace("/", "_"))
        temp_file = open(json_file, 'w')
        temp_file.write(json.dumps(direction_stops_times))
        temp_file.close()
        current_time = time.time()
        print(json_file, current_time - time_last)
        return direction_stops_times

    @classmethod
    def run_thread(cls, url):
        line = list(url.keys())[0]
        cls.get_route_directions_page(url.get(line))

    @classmethod
    def parse_traffic_links(cls, content):

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
        return lp.data

    @classmethod
    def parse_main_page(cls):
        r = requests.get(cls.MAIN_PAGE)
        content = "{}".format(r.content)

        urls = cls.parse_traffic_links(content)

        today = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
        if not os.path.exists(today):
            os.mkdir(today)

        pool = ThreadPool(4)
        pool.map(cls.run_thread, urls)
        return
        for url in urls:
            line = list(url.keys())[0]
            print(url)
            # cls.get_route_directions_page(url.get(line))
            t = threading.Thread(target=cls.get_route_directions_page, args = (url.get(line)))
            t.daemon = True
            t.start()
            return

if __name__ == '__main__':
    time_last = time.time()
    print("Started parsing the {} website!".format(PageParsing.MAIN_PAGE))
    PageParsing.parse_main_page()
    current_time = time.time()
    print("Parsed for {} seconds".format(current_time - time_last))
