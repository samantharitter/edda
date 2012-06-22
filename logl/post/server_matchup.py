# Copyright 2012 10gen, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/env python
import pymongo
import logging

def server_matchup(db, collName):
    """Given the mongoDB entries generated by logl,
    attempts to resolve any differences in server names
    or missing server names across entries.  Returns
    1 on success, -1 on failure"""
    # check for clock skew in tandem with server name checking
    # --> check if coll.servers has any entries where server_num == server_name
    logger = logging.getLogger(__name__)

    servers = db[collName + ".servers"]
    entries = db[collName + ".entries"]
    server_count = servers.find().count()

    # no servers
    if server_count == 0:
        return 1

    # no unknown servers
    unknowns = servers.find({"server_name" : "unknown"})
    unknown_count = unknowns.count()
    if unknown_count == 0:
        return 1

    # all servers are unknown
    # this case could probably be handled for cases where server_count > 1
    logger.debug("attempting to name {0} unnamed servers".format(unknown_count))
    if server_count == unknown_count:
        return -1

    # find a list of all unnamed servers being talked about
    unmatched_names = []
    cursor = entries.distinct("info.server")
    for name in cursor:
        if name == "self":
            continue
        if servers.find_one({"server_name" : name}):
            continue
        unmatched_names.appen(name)

    # if there are no free names and still unknown servers, failure.
    if len(unmatched_names) == 0:
        return -1

    failures = 0
    candidates = {}

    # match up the names!
    for unknown in unknowns:
        for name in unmatched_names:
            # if we're on the last name, winner!!
            if len(name) == 1:
                candidates[str(1)] = name
                break
            # in the .servers coll, replace server_name for unknown with name
            # in the .entries coll, replace origin_server from unknown["server_num"] to name
            # run the clock skew algorithm
            # store name and highest weight clock skew from this round (with first named server)
            # set the entries back to the original server_num
        # select candidate with highest weight!
        keys = candidates.keys()
        keys.sort()
        winner = candidates[keys[0]]
        # update db entries accordingly with winning name
        unknown["server_name"] = winner
        servers.save(unknown)
        entries.update({"origin_server" : unknown["server_num"]}, {"$set" : {"origin_server" : winner}})
        # run clock skew algorithm anew
        server_clock_skew()
        # remove name from the list of unmatched_names
        unmatched_names.remove(winner)
        candidates = {}

    if failures > 0:
        logger.info("Unable to match names for {0} of {1} unnamed servers".format(failures, unknown_count))
        return -1
    logger.info("Successfully named {0} unnamed servers".format(unknown_count))
    return 1

