# encoding: utf-8

# Import #
##########

import os
import sqlite3
import time
from settings import *
from modules import *
import logging
from logging.handlers import TimedRotatingFileHandler

# Variables #
#############

# Reads in configuration file

data = config.read_config_json()
msg = messages.read_msg_json()

# Logging #
###########

consoleFormatter = logging.Formatter("%(asctime)s: %(message)s",datefmt="%I:%M:%S %p")
fileFormatter = logging.Formatter("%(asctime)s %(levelname)s - %(message)s",datefmt="%I:%M:%S %p")
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)
fileHandler = TimedRotatingFileHandler("logs/pointbot.log",when="midnight",backupCount=14)
fileHandler.setFormatter(fileFormatter)
rootLogger.addHandler(fileHandler)
consoleHandler = logging.StreamHandler()
if data["loglevel"] == "debug":
    consoleHandler.setLevel(logging.DEBUG)
elif data["loglevel"] == "info":
    consoleHandler.setLevel(logging.INFO)
else:
    consoleHandler.setLevel(logging.WARNING)
consoleHandler.setFormatter(consoleFormatter)
rootLogger.addHandler(consoleHandler)

# Functions #
#############

def pointsbot(data):
    # Screen Formatting
    os.system("cls" if os.name == "nt" else "clear")
    print "Points bot initiated."
    data = config.check_environment(data)

    # Account Module
    r = account.start(data)

    run = True
    database.start(data["database"])

    while run:

        # Commands Module
        #commands.start(data,msg,r)

        # Comments Module
        comments.start(data,msg,r)

        # Wait 10 seconds
        wait_time = 10
        logging.info("Sleeping for %s seconds" % wait_time)
        time.sleep(wait_time)

# Run #
#######
# Stop reddit failures from killing the script
while True:
    try:
        pointsbot(data)
    except Exception as e:
        logging.error("Error code: %s" % e)


# EOF
