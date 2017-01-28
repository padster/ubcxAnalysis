import matplotlib
import matplotlib.pyplot as plt

import numpy as np
import random

import files

CATEGORY_MAP = {
  'course': '#',
  'chapter': '\\',
  'sequential': '|',
  'vertical': '-',
  'html': '>',
  'problem': '?',
  'video': '[ ]',
  'lti': '.',
}

SEQ_SCORES = []

# Map of element url_name -> list user IDs with that as their last event
LAST_EVENT_USERS_BY_ELEMENT = {};
def buildLastEventsByElement():
    # byUser = files.lastEventsByUserChronological();
    byUser = files.lastEventsByUserProgression()
    for userId, lastEvent in byUser.iteritems():
        axisKey = lastEvent['category'] + '::' + lastEvent['name']
        urlName = files.COURSE_AXIS_BY_EVENT_KEY[axisKey]['url_name']
        if urlName not in LAST_EVENT_USERS_BY_ELEMENT:
            LAST_EVENT_USERS_BY_ELEMENT[urlName] = [userId]
        else:
            LAST_EVENT_USERS_BY_ELEMENT[urlName].append(userId)


# Map of element to set of user ids who did it
USERS_BY_ELEMENT = {}
# Map of element to set of user ids who did it *or its children*
USERS_BY_ELEMENT_FULL = {}
def buildUsersForElements():
    for element in files.COURSE_AXIS_ROWS:
        eID = element['url_name']
        USERS_BY_ELEMENT[eID] = set()
        if eID in files.EVENT_LOG_BY_ELEMENT:
            for event in files.EVENT_LOG_BY_ELEMENT[eID]:
                USERS_BY_ELEMENT[eID].add(event['user_id'])

def buildUsersForElementsAndChildren(eID):
    USERS_BY_ELEMENT_FULL[eID] = USERS_BY_ELEMENT[eID]
    if eID in files.COURSE_AXIS_BY_PARENT:
        for child in files.COURSE_AXIS_BY_PARENT[eID]:
            childId = child['url_name']
            childUsers = buildUsersForElementsAndChildren(childId)
            USERS_BY_ELEMENT_FULL[eID] = USERS_BY_ELEMENT_FULL[eID].union(childUsers)
    return USERS_BY_ELEMENT_FULL[eID]

def printCourseTree(at, padding=''):
    row = files.COURSE_AXIS_BY_ID[at]
    cat = CATEGORY_MAP[row['category']] if row['category'] in CATEGORY_MAP else '~'
    eID = row['url_name']

    eventsForRow = files.eventsForCourseAxis(eID)
    eventsByUser = {}
    for event in eventsForRow:
        user = event['user_id']
        if not user in eventsByUser:
            eventsByUser[user] = []
        eventsByUser[user].append(event)
    avGrade = files.averageUserGrade(eventsByUser.keys())
    scoreSuffix = "" if avGrade < 0 else "with score %.2f" % (avGrade)
    users = len(USERS_BY_ELEMENT_FULL[eID]) or 0

    numLeft = 0
    scoreLeft = 0
    if row['url_name'] in LAST_EVENT_USERS_BY_ELEMENT:
        leftUsers = LAST_EVENT_USERS_BY_ELEMENT[row['url_name']]
        numLeft = len(leftUsers)
        scoreLeft = files.averageUserGrade(leftUsers)

    categoryFilter = None # ['#', '\\', '|']
    if categoryFilter is None or cat in categoryFilter:
        print ('%s (%s) %s - %d users, %d left (%.2f)') % (padding, cat, row['name'], users, numLeft, scoreLeft)
        # print ('%s (%s) %s - %d users, %d left (%.2f)') % (padding, cat, row['name'], users, numLeft, scoreLeft)
        # print ('%s (%s) %s - %d events from %d users %s') % (padding, cat, row['name'], len(eventsForRow), users, scoreSuffix)

    if cat == '|' and avGrade >= 0:
        SEQ_SCORES.append(avGrade)

    if at in files.COURSE_AXIS_BY_PARENT:
        for child in files.COURSE_AXIS_BY_PARENT[at]:
            printCourseTree(child['url_name'], padding + '  ')

if __name__ == '__main__':
    random.seed(4321)
    np.random.seed(4321)
    print "Reading course axis..."
    files.cacheCourseAxis()
    print "Reading user data..."
    files.cacheUsers()
    # NEEDS TO GO AFTER COURSE AXIS PARSE
    print "Reading event log..."
    files.cacheEventLog()
    print "Generating data..."
    buildLastEventsByElement();
    buildUsersForElements();
    buildUsersForElementsAndChildren(files.ROOT_AXIS)

    printCourseTree(files.ROOT_AXIS)

    # plt.plot(SEQ_SCORES)
    # plt.show()
