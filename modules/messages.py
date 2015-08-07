# Messages #
############

# Import

import praw
import json
import logging
import time

# VARIABLES LEGEND
#
# Use this section to build your messages. You want the information AFTER the equal sign (=) to put in your messages.
#
# subreddit = data["running_subreddit"]
# username = data["running_username"]
# token = msg["token"]
#

# Functions

# Reads in the json for the messages
def read_msg_json():
    with open("settings/messages.json","r") as json_msg:
        msg = json.load(json_msg)
    return msg

