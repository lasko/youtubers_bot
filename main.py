# encoding: UTF-8
# Reddit /r/youtubers Bot -- Designed by: /u/bmheight

# Import #
##########
import os
import praw
from settings import config
import time
from modules import account, comments, messages, submissions
import logging
from logging.handlers import TimedRotatingFileHandler
import sqlite3

# Read in the configuration
data = config.read_yaml_config('./settings/config.yml')
msg = messages.read_msg_yaml('./settings/messages.yml')

# Logging #
###########

consoleFormatter = logging.Formatter("%(asctime)s: %(message)s",datefmt="%I:%M:%S %p")
fileFormatter = logging.Formatter("%(asctime)s %(levelname)s - %(message)s",datefmt="%I:%M:%S %p")
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)
fileHandler = TimedRotatingFileHandler("logs/pointsbot.log",when="midnight",backupCount=14)
fileHandler.setFormatter(fileFormatter)
rootLogger.addHandler(fileHandler)
consoleHandler = logging.StreamHandler()
if data["settings"]["loglevel"] == "debug":
    consoleHandler.setLevel(logging.DEBUG)
elif data["settings"]["loglevel"] == "info":
    consoleHandler.setLevel(logging.INFO)
else:
    consoleHandler.setLevel(logging.WARNING)
consoleHandler.setFormatter(consoleFormatter)
rootLogger.addHandler(consoleHandler)



# Functions #
#############

def pointsbot(data,placeholder_submission,placeholder_comment):
    os.system('cls' if os.name == "nt" else "clear")
    print "Points system tracker enabled"

    data = config.read_yaml_config('./settings/config.yml')

    # Setup database
    sql = sqlite3.connect(data["settings"]["database"], isolation_level=None)
    logging.info("Loaded SQL Database")

    cur = sql.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS points(AMOUNT, NAME)")
    cur.execute("CREATE TABLE IF NOT EXISTS alreadydone(THREADID)")
    logging.info("Loaded SQL Tables")

    sql.commit()

    # Account Module
    r = account.start(data)

    run = True

    while run:
        # Commands module
        # commands.start(data,msg,r)

        # Submissions Module
        placeholder_submission = submissions.start(data,msg,r,cur,placeholder_submission)

        # Comments Module
        placeholder_comment = comments.start(data,msg,r,cur,placeholder_comment)


        # Wait 10 seconds
        wait_time = 10
        logging.info("Sleeping for %s seconds" % wait_time)
        time.sleep(wait_time)

    sql.commit()
    sql.close()

# Main #
########

placeholder_submission = None
placeholder_comment = None

# Prevent reddit failures from killing the bot
while True:
    try:
        pointsbot(data,placeholder_submission,placeholder_comment)
    except Exception as e:
        logging.error("Error code: %s" % e)
