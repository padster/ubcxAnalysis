import datetime
import dateutil.parser
import files
import json
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from pprint import pprint
import random

"""
play_video:
"{""code"": ""yiQ19RO8v-o"", ""id"": ""a7c7f011a95f4fb69746b22ba6a8d1a4"", ""currentTime"": 224.39}"
seek_video
"{""code"": ""BC8n1vUHC8I"", ""type"": ""onSlideSeek"", ""id"": ""3cddd9c9009d464598173d15c01317a7"", ""new_time"": 106, ""old_time"": 128.818}"
load_video
"{""code"": ""2elmjjKQeU0"", ""id"": ""eb19b47043b145f8923dda17716b25f9""}"
pause_video
"{""code"": ""uExkIfBCXJs"", ""id"": ""4f49c33c92cb4ce9a8edb7f2086cc7e4"", ""currentTime"": 212.654125}"
speed_change_video
"{""current_time"": 7.45729, ""old_speed"": ""1.0"", ""code"": ""049KP2lEoNE"", ""id"": ""9e79376f6cb7410197eddc78bdccb570"", ""new_speed"": ""1.50""}"
stop_video
"{""code"": ""mobile"", ""id"": ""729be66e008442a79bdc7fa473cf791b"", ""currentTime"": 0}"
"""

def plotVideo(events):
    if len(events) == 0:
        return [], []
    EPS = 0.01
    wallTimes = []
    videoTimes = []
    for event in events:
        if event['type'] == 'seek':
            wallTimes.append(event['wallAt'] - EPS)
            videoTimes.append(event['seekFrom'] - EPS)
        wallTimes.append(event['wallAt'] - EPS)
        videoTimes.append(event['videoAt'] - EPS)
    if len(wallTimes) == 0:
        return [], []
    if np.max(wallTimes) > 2000:
        # they came back after a long time?
        return [], []
    plt.plot(wallTimes, videoTimes)
    return wallTimes, videoTimes

def showPlots(reworkedEvents, eventName):
    maxVideoTime = 0
    maxWallTime = 0
    for userId, events in reworkedEvents.iteritems():
        wallTimes, videoTimes = plotVideo(events)
        if len(wallTimes) == 0:
            continue
        maxWallTime = max(maxWallTime, int(np.max(wallTimes) + 0.9))
        maxVideoTime = max(maxVideoTime, int(np.max(videoTimes) + 0.9))

    xBuff, yBuff = 10, 5
    plt.axis([-xBuff, maxWallTime + xBuff, -yBuff, maxVideoTime + yBuff])
    pad = 0.05
    plt.subplots_adjust(left=pad, right=1.0-pad, top=1.0-pad, bottom=pad, hspace=pad)
    plt.get_current_fig_manager().window.showMaximized()
    plt.title(eventName)
    plt.ylabel('Video position (sec)')
    plt.xlabel('Wall time (sec)')
    plt.show()

VIDEO_TYPES = ['load_video', 'play_video', 'pause_video', 'stop_video', 'seek_video', 'speed_change_video']

EPOCH = datetime.datetime.utcfromtimestamp(0)
def iso8601toSec(iso8601):
    dt = dateutil.parser.parse(iso8601)
    utc_naive  = dt.replace(tzinfo=None) - dt.utcoffset()
    return int((utc_naive - EPOCH).total_seconds())

def eventSort(a, b):
    secDelta = a['atSec'] - b['atSec']
    if secDelta != 0:
        return secDelta
    return VIDEO_TYPES.index(a['type']) - VIDEO_TYPES.index(b['type'])

def calcVideoTime(data, event, lastData, speed=1):
    if lastData == None:
        return 0
    if event is not None:
        if 'currentTime' in event:
            return float(event['currentTime'])
        if 'current_time' in event:
            return float(event['current_time']) # lol, whoops
    if data['type'] == "seek":
        return data['seekTo']
    if data['type'] == "load": # ignored
        return lastData['videoAt']
    if lastData['type'] == "pause":
        return lastData['videoAt']
    if lastData['type'] == "play" or lastData['type'] == "seek":
        return lastData['videoAt'] + (data['wallAt'] - lastData['wallAt']) * speed
    if lastData['type'] == "stop":
        return 0
    return None

def reworkEvents(events):
    reworked = []

    lastStartTime = 0
    previousRelative = 0
    lastRelative = 0
    lastWasLoad = False
    videoTime = 0
    lastData = None
    currentSpeed = 1.0

    events = sorted(events, cmp=eventSort)
    for event in events:
        if event['type'] == 'load_video':
            lastRelative = previousRelative
            lastWasLoad = True
            continue
        if lastWasLoad:
            lastStartTime = event['atSec']
            lastWasLoad = False
        relativeTime = event['atSec'] - lastStartTime + lastRelative
        previousRelative = relativeTime
        data = {
            'wallAt': relativeTime,
            'type': event['type'][:-6],
        }
        if event['type'] in ['play_video', 'pause_video', 'stop_video']:
            pass
        elif event['type'] == 'seek_video':
            data.update({
                'seekFrom': float(event['old_time']),
                'seekTo': float(event['new_time']),
            })
        elif event['type'] == 'speed_change_video':
            data.update({
                'speedFrom': float(event['old_speed']),
                'speedTo': float(event['new_speed']),
            })
            currentSpeed = data['speedTo']
        data['videoAt'] = calcVideoTime(data, event, lastData, currentSpeed)
        reworked.append(data)
        lastData = data
        # pprint(data)
        # print "  %d\t%s\t%s" % (event['atSec'], event['type'], str(event))
    return reworked

def processVideoLogs(videoID):
    allEventsForVideoByUser = {}
    for row in files.EVENT_LOG_ROWS:
        rowUser = row['user_id']
        if row['event_type'].endswith('_video'):
            event = json.loads(row['event'])
            if event['id'] == videoID:
                event['type'] = row['event_type']
                event['atSec'] = iso8601toSec(row['time'])
                if not rowUser in allEventsForVideoByUser:
                    allEventsForVideoByUser[rowUser] = []
                allEventsForVideoByUser[rowUser].append(event)

    # Simple: 1818
    # With pause: 762
    # Hard: 662
    # With speed change: 1308
    reworkedEvents = {}
    for userID, events in allEventsForVideoByUser.iteritems():
        reworkedEvents[userID] = reworkEvents(events)
    showPlots(reworkedEvents, files.COURSE_AXIS_BY_ID[videoID]['name'])


def printVideos():
    for row in files.COURSE_AXIS_ROWS:
        if row['category'] == 'video':
            print ("%s :: %s") % (row['url_name'], row['name'])

if __name__ == '__main__':
    random.seed(4321)
    np.random.seed(4321)
    print "Reading course axis..."
    files.cacheCourseAxis(True)
    print "Reading event log..."
    files.cacheEventLog()

    printVideos()
    print "\nWhich video?"
    videoID = raw_input()
    # videoID = "8eca34b3e97c4cbea92eb970c610d12c"

    print "Processing video %s..." % (videoID)
    processVideoLogs(videoID)
