#!/usr/bin/env python

# anatomy of a clock skew document:
# document = {
#    "type" = "clock_skew"
#    "server" = "name"
#    "partners" = {
#          server_name : timedelta,
#          }
#     }

import pymongo
import logging
from datetime import datetime
from datetime import timedelta

def server_clock_skew(db, collName):
    """Given the mongodb entries generated by logl,
    attempts to detect and resolve clock skew
    across different servers.  Returns 1 on success,
    -1 on failure"""
    logger = logging.getLogger(__name__)
    for doc_a in collName["servers"].find():
        a = doc_a["server_name"]
        if a == "unknown":
            logger.debug("Skipping unknown server")
            continue
        skew_a = collName["clock_skew"].find_one({"server": a})
        if not skew_a:
            skew_a = clock_skew_doc(a)
        for doc_b in collName["servers"].find():
            b = doc_b["server_name"]
            logger.info("Finding clock skew for {0} - {1}...".format(a, b))
            if b == "unknown":
                logger.debug("Skipping unknown server")
                continue
            if a == b:
                logger.debug("Skipping identical server")
                continue
            if skew_a["partners"][b]:
                logger.debug("Already found clock skew for {0} - {1}".format(a, b))
                continue
            skew_a["partners"][b] = detect(a, b, db, collName)
            skew_b = collName["clock_skew"].find_one({"server":b})
            if not skew_b:
                skew_b = clock_skew_doc(b)
            # change this to use a sign convention
            skew_b["partners"][a] = skew_a["partners"][b]
    return -1


def detect(a, b, db, collName):
    """Detect any clock skew between a and b,
    and return it as a timedelta object.  If
    unable to detect skew, return None.  This is different
    from 0 skew, which will be a timedelta with value 0"""
    cursor_a = collName["entries"].find({"type" : "status", "origin_server" : a, "info.server" : b})
    cursor_b = collName["entries"].find({"type" : "Status", "origin_server" : b, "info.server" : b})
    cursor_a.sort("date")
    cursor_b.sort("date")
    logger = logging.getLogger(__name__)
    logger.debug("Detecting clock skew for pair {0} - {1}...".format(a, b))
    if not cursor_a.hasNext():
        return None
    if not cursor_b.hasNext():
        return None
    a_1 = cursor_a.next()
    b_1 = cursor_b.next()
    min_time = timedelta(seconds=2)
    # take and compare two consecutive entries from each cursor
    while True:
        logger.debug("Using next set of entries")
        if not cursor_a.hasNext():
            return None
        if not cursor_b.hasNext():
            return None
        a_2 = cursor_a.next()
        b_2 = cursor_b.next()
        # if first entries do not match, advance A
        while a_1["state_code"] != b_1["state_code"]:
            logger.debug("first entries do not match")
            a_1 = a_2
            if not cursor_a.hasNext():
                return None
            a_2 = cursor_a.next()
        # if first entries match but not second ones, advance A and B
        if (a_1["state_code"] == b_1["state_code"]) and (a_2["state_code"] != b_2["state_code"]):
            logger.debug("first entries match, but not second ones")
            a_2 = cursor_a.next()
            b_2 = cursor_b.next()
        # if both first and second entries match, take clock skew
        # (fix me so I work better please...)
        if (a_1["info"]["state_code"] == b_1["info"]["state_code"]) and (a_2["info"]["state"] == b_2["info"]["state"]):
            logger.debug("Both entries match!  Calculating clock skew")
            td1 = a_1["date"] - b_1["date"]
            td2 = a_2["date"] - b_2["date"]
            # if td1 and td2 are wildly different, try again
            diff = td1 - td2
            if abs(diff) < min_time:
                logger.debug("td1 and td2 agree.  Big enough for clock skew?")
                # they agree.  But big enough for clock skew?
                if abs(td1) > min_time:
                    logger.debug("clock skew found!  Returning {0}".format(td1))
                    return td1 # or return the smaller of the two?
        a_1 = a_2
        b_1 = b_2


def clock_skew_doc(name):
    """Create and return an empty clock skew doc
    for this server"""
    logger = logging.getLogger(__name__)
    logger.debug("creating empty clock skew doc")
    doc = {}
    doc["server_name"] = name
    doc["type"] = "clock_skew"
    doc["partners"] = {}
    return doc

