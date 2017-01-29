import matplotlib
import matplotlib.pyplot as plt

import numpy as np
import random

import files
import userStats

# Add logic here to determine which users we want to include or exclude:
def filterUser(user):
    if user['isstaff'] == 'TRUE':
        return False
    return user['education'] == 'high_school'
    #return True

def filterUsers(users):
    return {userID for userID in users if userID in files.USER_ROWS_BY_ID and filterUser(files.USER_ROWS_BY_ID[userID])}

# Generate visual data for single element
def printElement(element, cat, stayUsers, leaveUsers, padding):
    eID = element['url_name']
    userCount = len(stayUsers) + len(leaveUsers)
    leaveCount = len(leaveUsers)
    leaveGrade = files.averageUserGrade(leaveUsers)
    if leaveCount > 0:
        print ('%s (%s) %s - %d users, %d left (%.2f)') % (padding, cat, element['name'], userCount, leaveCount, leaveGrade)

# Useful representations of category types
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

# Generate visual data for entire heirarchy
def printCourseTree(eID, padding=''):
    row = files.COURSE_AXIS_BY_ID[eID]
    cat = CATEGORY_MAP[row['category']] if row['category'] in CATEGORY_MAP else '~'

    categoryFilter = None #['#', '\\', '|']
    if categoryFilter is None or cat in categoryFilter:
        allUsers = filterUsers(userStats.allUsersForElement(eID))
        leaveUsers = filterUsers(userStats.leaveUsersForElement(eID))
        stayUsers = allUsers.difference(leaveUsers)
        printElement(row, cat, stayUsers, leaveUsers, padding)

    if eID in files.COURSE_AXIS_BY_PARENT:
        for child in files.COURSE_AXIS_BY_PARENT[eID]:
            printCourseTree(child['url_name'], padding + '  ')

# Actual code run...
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
    userStats.buildUsersForElements(files.ROOT_AXIS);
    userStats.buildLastEventUsersByElement();
    # and...visualize!
    printCourseTree(files.ROOT_AXIS)
