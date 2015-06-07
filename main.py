from flask import Flask
import datetime
app = Flask(__name__)


@app.route('/tramway/<number>/')
@app.route('/tramway/<number>/<date>')
def tramway(number, date=datetime.date.today()):
    return "Tramway №{} for the day {}".format(number, date), 404


@app.route('/bus/<number>/')
@app.route('/bus/<number>/<date>')
def bus(number, date=datetime.date.today()):
    return "Bus №{} for the day {}".format(number, date), 404


@app.route('/trolley/<number>/')
@app.route('/trolley/<number>/<date>')
def trolley(number, date=datetime.date.today()):
    return "Trolley №{} for the day {}".format(number, date), 404


if __name__ == '__main__':
    app.run()
