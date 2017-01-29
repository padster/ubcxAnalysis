import csv
import numpy as np

COURSE_PATH = 'UBCx__Climate101x__3T2015_cleaned'
# COURSE_PATH = 'UBCx__China300_1x__3T2015_cleaned'
CLIMATE_LOG = 'data/' + COURSE_PATH + '/tracklog_cleaned.tsv'
COURSE_AXIS = 'data/' + COURSE_PATH + '/course_axis.tsv'
USER_DATA = 'data/' + COURSE_PATH + '/person_course_cleaned.tsv'

USER_ROWS = []
USER_ROWS_BY_ID = {}

def cacheUsers():
    with open(USER_DATA, 'rb') as inputFile:
        log = csv.DictReader(inputFile, delimiter='\t')
        for row in log:
            USER_ROWS.append(row)
            USER_ROWS_BY_ID[row['user_id']] = row

def averageUserGrade(users):
    scores = []
    for user in users:
        if user not in USER_ROWS_BY_ID:
            continue
        userRow = USER_ROWS_BY_ID[user]
        if userRow['isstaff'] == 'TRUE':
            continue
        if userRow['grade'] == 'NA':
            continue
        scores.append(float(userRow['grade']))
    if len(scores) == 0:
        return -1.0
    return np.mean(scores)

COURSE_AXIS_ROWS = []
COURSE_AXIS_BY_ID = {}
COURSE_AXIS_BY_PARENT = {}
COURSE_AXIS_BY_EVENT_KEY = {}
ROOT_AXIS = None

def cacheCourseAxis():
    global ROOT_AXIS
    with open(COURSE_AXIS, 'rb') as inputFile:
        log = csv.DictReader(inputFile, delimiter='\t')
        for row in log:
            row['element_order'] = int(row['element_order']) # lol

            COURSE_AXIS_ROWS.append(row)
            COURSE_AXIS_BY_ID[row['url_name']] = row

            eventKey = row['category'] + '::' + row['name']

            if not eventKey in COURSE_AXIS_BY_EVENT_KEY:
                COURSE_AXIS_BY_EVENT_KEY[eventKey] = []
            COURSE_AXIS_BY_EVENT_KEY[eventKey].append(row)

            if row['parent'] == 'NA':
                print row['url_name']
                ROOT_AXIS = row['url_name']
            else:
                if not row['parent'] in COURSE_AXIS_BY_PARENT:
                    COURSE_AXIS_BY_PARENT[row['parent']] = []
                COURSE_AXIS_BY_PARENT[row['parent']].append(row)


#replace with searching course_axis_by_ID with getuniqueID(event)
def elementForEvent(event):
    elementKey = getUniqueID(event)
    if elementKey not in COURSE_AXIS_BY_ID:
        return None
    return COURSE_AXIS_BY_ID[elementKey]


def getUniqueID(event):
    axisKey = event['category'] + '::' + event['name']
    matchingIDs = []

    if not axisKey in COURSE_AXIS_BY_EVENT_KEY:
	    return None

    for element in COURSE_AXIS_BY_EVENT_KEY[axisKey]:
        matchingIDs.append(element['url_name'])

    for id in matchingIDs:
        if id in event['event']:
           return id




EVENT_LOG_ROWS = []
EVENT_LOG_BY_ELEMENT = {}
EVENT_LOG_BY_USER = {}
EVENT_LOG_BY_ID = {}

def cacheEventLog():
    with open(CLIMATE_LOG, 'rb') as inputFile:
        log = csv.DictReader(inputFile, delimiter='\t')
        for row in log:
            EVENT_LOG_ROWS.append(row)

            element = elementForEvent(row)
            if element is None:
                continue;
            if not element['url_name'] in EVENT_LOG_BY_ELEMENT:
                EVENT_LOG_BY_ELEMENT[element['url_name']] = []
            EVENT_LOG_BY_ELEMENT[element['url_name']].append(row)

            userId = row['user_id']
            if not userId in EVENT_LOG_BY_USER:
                EVENT_LOG_BY_USER[userId] = []
            EVENT_LOG_BY_USER[userId].append(row)

def lastEventsByUserChronological():
    lastEvents = {}
    for userId, user in USER_ROWS_BY_ID.iteritems():
        if not userId in EVENT_LOG_BY_USER:
            continue
        events = EVENT_LOG_BY_USER[userId]
        if len(events) == 0:
            continue
        lastEvents[userId] = events[-1]
    return lastEvents

def lastEventsByUserProgression():
    lastEvents = {}
    for userId, user in USER_ROWS_BY_ID.iteritems():
        if not userId in EVENT_LOG_BY_USER:
            continue
        events = EVENT_LOG_BY_USER[userId]
        if len(events) == 0:
            continue

        lastEventElement = -1
        lastEvent = None

        #replace by axisKey = uniqueID(event), if axisKey not in COURSE_AXIS_BY_ID
        for event in events:
            axisKey = getUniqueID(event)
            if axisKey not in COURSE_AXIS_BY_ID:
                continue # oops?
            element = COURSE_AXIS_BY_ID[axisKey]
            if lastEventElement < element['element_order']:
                lastEventElement = element['element_order']
                lastEvent = event

        if lastEvent is not None:
            lastEvents[userId] = lastEvent
    return lastEvents


#replace by changing axisKey to axis['urlName']
def eventsForCourseAxis(axisId):
    if axisId not in COURSE_AXIS_BY_ID:
        return []
    axis = COURSE_AXIS_BY_ID[axisId]
    axisKey = axis['url_name']
    if not axisKey in EVENT_LOG_BY_ELEMENT:
        return []
    return EVENT_LOG_BY_ELEMENT[axisKey]
