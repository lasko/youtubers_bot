# Login #
#########

# Import

import os
import praw
import logging
import time

# Variables

# Functions

def start(data):
    logging.debug("Starting Module: Account")
    return login(data)

def login(data):
    r = praw.Reddit(user_agent = data["running_username"] + ": Reddit Points System Moderator")
    login_attempt = True
    while login_attempt:
        try:
            logging.info(data["running_username"] + ": Attempting Login")
            r.login(data["running_username"],data["running_password"])
            logging.info("Login Successful")
            login_attempt = False
        except:
            login_wait = 300
            logging.info("Login Failed - Trying again in %s seconds" % login_wait)
            time.sleep(login_wait)
    return r

# EOF
