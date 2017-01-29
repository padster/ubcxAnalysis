#import matplotlib
#import matplotlib.pyplot as plt

import numpy as np
import random

import files
import userStats

EXCLUDE_SURVEYS = True

SEQUENTIAL_USERS = []

# Add logic here to determine which users we want to include or exclude:
def filterUser(user):
    if user['isstaff'] == 'TRUE':
        return False
    # preMOOC = user['entryTest']['In how many MOOCs have you participated at least partially?']
    # return preMOOC in ['1-2.', '3-7.', '8 or more.']

    # return 'prepost' in user
    # return 'exitTest' in user
    return user['nforum_posts'] != "NA"
    # return user['grade'] > 0.5
    # return user['education'] == 'high_school'
    # return True

def filterUsers(users):
    return {userID for userID in users if userID in files.USER_ROWS_BY_ID and filterUser(files.USER_ROWS_BY_ID[userID])}

# Generate visual data for single element
def printElement(element, cat, stayUsers, leaveUsers, padding):
    eID = element['url_name']
    userCount = len(stayUsers) + len(leaveUsers)
    leaveCount = len(leaveUsers)
    leaveGrade = files.averageUserGrade(leaveUsers)
    if cat == '|':
        print ('%s (%s) %s - %d users, %d left (%.2f)') % (padding, cat, element['name'], userCount, leaveCount, leaveGrade)
        SEQUENTIAL_USERS.append(userCount)
    # if leaveCount > 0:


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
    files.cacheCourseAxis(EXCLUDE_SURVEYS)
    print "Reading user data..."
    files.cacheUsers()
    files.addEntryExitDataToUsers()

    # NEEDS TO GO AFTER COURSE AXIS PARSE
    print "Reading event log..."
    files.cacheEventLog()
    print "Generating data..."
    userStats.buildUsersForElements(files.ROOT_AXIS);
    userStats.buildLastEventUsersByElement();
    # and...visualize!
    printCourseTree(files.ROOT_AXIS)

    if len(SEQUENTIAL_USERS) > 0:
        plt.get_current_fig_manager().window.showMaximized()
        plt.plot(SEQUENTIAL_USERS)
        plt.show()
