import files

# Map of element to set of user ids who did it
USERS_BY_ELEMENT = {}
def buildUsersForElements(rootID):
    for element in files.COURSE_AXIS_ROWS:
        eID = element['url_name']
        USERS_BY_ELEMENT[eID] = set()
        if eID in files.EVENT_LOG_BY_ELEMENT:
            for event in files.EVENT_LOG_BY_ELEMENT[eID]:
                USERS_BY_ELEMENT[eID].add(event['user_id'])
    # Now that last users at each element is known, add each child's to parent's:
    buildUsersForElementsAndChildren(rootID)

# Map of element to set of user ids who did it *or its children*
USERS_BY_ELEMENT_FULL = {}
def buildUsersForElementsAndChildren(eID):
    USERS_BY_ELEMENT_FULL[eID] = USERS_BY_ELEMENT[eID]
    if eID in files.COURSE_AXIS_BY_PARENT:
        for child in files.COURSE_AXIS_BY_PARENT[eID]:
            childId = child['url_name']
            childUsers = buildUsersForElementsAndChildren(childId)
            USERS_BY_ELEMENT_FULL[eID] = USERS_BY_ELEMENT_FULL[eID].union(childUsers)
    return USERS_BY_ELEMENT_FULL[eID]

# Map of element url_name -> set of user IDs with that as their last event
LAST_EVENT_USERS_BY_ELEMENT = {};
def buildLastEventUsersByElement():
    byUser = files.lastEventsByUserProgression()
    for userId, lastEvent in byUser.iteritems():
        urlName = files.getUniqueID()
        if urlName not in LAST_EVENT_USERS_BY_ELEMENT:
            LAST_EVENT_USERS_BY_ELEMENT[urlName] = set()
        LAST_EVENT_USERS_BY_ELEMENT[urlName].add(userId)

# Safe getters
def allUsersForElement(eID):
    return USERS_BY_ELEMENT_FULL[eID] if eID in USERS_BY_ELEMENT_FULL else set()

def leaveUsersForElement(eID):
    return LAST_EVENT_USERS_BY_ELEMENT[eID] if eID in LAST_EVENT_USERS_BY_ELEMENT else set()
