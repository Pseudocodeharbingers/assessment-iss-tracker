from flask import Flask, Response, json, render_template
import json
from flask import request
import requests
from datetime import datetime
from datetime import timedelta, date, time
import time
from urllib.request import urlopen
from json2html import *


app = Flask(__name__)

def get_current_pose():
    response = requests.get('https://api.wheretheiss.at/v1/satellites/25544')
    return response.json()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/location')
def location():
    getdate = request.args.get('Date')
    gettime = request.args.get('Time')
    LatestTime = datetime.strptime(gettime, '%H:%M')
    ConvertTime = LatestTime.time()
    CurrentTime = datetime.combine(date.min, ConvertTime) - datetime.min
    timedeltaobj = timedelta(hours=1)
    StartTimeLess = CurrentTime - timedeltaobj
    StartTimeMore = CurrentTime + timedeltaobj
    TimeinEpochLess = []
    TimeinEpochMore = []
    NewStartTimeLess = []
    NewStartTimeMore = []

    while StartTimeLess < CurrentTime:
        StartTimeLess = StartTimeLess + timedelta(minutes=10)
        NewStartTimeLess.append(str(StartTimeLess))
        t = time.mktime(time.strptime(getdate + " " + str(StartTimeLess), "%Y-%m-%d %H:%M:%S"))
        TimeinEpochLess.append(int(t))

    while StartTimeMore > CurrentTime:
        StartTimeMore = StartTimeMore - timedelta(minutes=10)
        NewStartTimeMore.append(str(StartTimeMore))
        t = time.mktime(time.strptime(getdate + " " + str(StartTimeMore), "%Y-%m-%d %H:%M:%S"))
        TimeinEpochMore.append(int(t))

    TimeinEpoch = TimeinEpochLess + TimeinEpochMore

    strTimeinEpoch = list(map(str, TimeinEpoch))
    FinalTimeinEpoch = ','.join(strTimeinEpoch)
    url = "https://api.wheretheiss.at/v1/satellites/25544/positions?timestamps=" + FinalTimeinEpoch + "&units=miles"
    response = urlopen(url)
    data_json = json.loads(response.read())

    url_people = "http://api.open-notify.org/astros.json"
    response_people = urlopen(url_people)
    data_json_people = json.loads(response_people.read())

    return render_template('location.html', Date1=datetime.strptime(getdate, '%Y-%m-%d').date(),
                           Time1=gettime, NewStartTimeLess=list(NewStartTimeLess),
                           NewStartTimeMore=list(NewStartTimeMore),
                           listTime=FinalTimeinEpoch.split(','),
                           people=json2html.convert(json=data_json_people),
                           url=url, test=json2html.convert(json=data_json),
                           initial_pose=get_current_pose())

@app.route('/api/pose')
def pose_stream():

    def __generate__(delay=1.0):
        while True:
            response = get_current_pose()
            response = json.dumps(response)
            yield f"data:{response}\n\n"
            time.sleep(delay)

    return Response(__generate__(), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug = True)
