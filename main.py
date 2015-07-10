from flask import Flask
import datetime
import time
import os.path
app = Flask(__name__)


@app.route('/<transport>/<number>/')
@app.route('/<transport>/<number>/<display_date>/')
def transport(transport, number, display_date=datetime.date.today()):

    if transport != "tramway" and transport != "bus" and transport != "trolley":
        return "Transport {} not supported".format(transport), 400

    try:
        dt = time.strptime(display_date, "%Y-%m-%d")
        if display_date > datetime.date.today().strftime("%Y-%m-%d"):
            display_date = datetime.date.today()
    except Exception:
        return "Date format must be Y-m-d".format(), 400

    json_file = "{}/{}_{}.json".format(display_date, transport, number)
    print(json_file)
    if not os.path.isfile(json_file):
        return "Information about {} {} {} Not Found".format(transport, number, display_date), 404

    return open(json_file, "r").read(), 200


if __name__ == '__main__':
    app.run()
