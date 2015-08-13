# encoding: UTF-8


# Import #
##########

import re
import logging
import time
from pprint import pprint

# Variables #
#############

history = []

# Functions #
#############

# Start the Comments module
def start(data,msg,r,cur,placeholder_comment):
    logging.debug("Starting Module: Comments")
    # Get the subreddit object)
    subreddit = get_sub(r,data["settings"]["subreddit"])
    if placeholder_comment:
        posts = sub_get_comments(subreddit, placeholder_comment)
    else:
        posts = sub_get_comments(subreddit)
    process(data,msg,r,posts,cur,placeholder_comment)
    return placeholder_comment

# Gets the subreddit object from reddit
def get_sub(r,sub_name):
    logging.debug("Getting Subreddit")
    logging.info("Running in %s" % sub_name)
    return r.get_subreddit(sub_name)

# Gets the newest comments from the subreddit
def sub_get_comments(subreddit, placeholder_comment = None):
    logging.debug("Getting Comments")
    if placeholder_comment:
        logging.debug("FOUND PLACE HOLDER!")
        return subreddit.get_comments(placeholder = placeholder_comment)
    else:
        return subreddit.get_comments(limit=100) # Limits submissions retrieved

# Processes the comments
def process(data,msg,r,posts,cur,placeholder_comment):
    logging.debug("Processing Post Comments")
    bot_name = str(data["settings"]["username"]).lower()
    for post in posts:
        pid = post.id
        pauthor = get_author(post)
        pbody = post.body.lower()
        if pauthor != "[DELETED]":
            comment_checked_status = check_alreadydone(pid,cur)
            if not comment_checked_status:
                logging.debug("Comment has not been checked. Checking now.")
                if pbody in data["commands"]["userlevel"]:
                    for command in data["commands"]["userlevel"]:
                        result = pbody.find(command)
                        if result != -1:
                            logging.debug("Command: %s -- found in comment" %(command))
                            points = get_points(post.author.name,cur)
                            if points == False:
                                insert_user(post.author.name,cur)
                                points = get_points(post.author.name,cur)
                            if points == None:
                                points = 0
                            # Reply to the user with their account balance.
                            logging.debug("Replying with --  User: %s currently has a balance of %s" %(post.author.name, points))
                            r.send_message(post.author.name, "Account Balance: %s" %(points), msg["account_balance"] %(data["settings"]["subreddit"],points),from_sr="/r/"+data['settings']['subreddit'],captcha = None)
                            #post.reply("User: %s -- currently has a balance of %s." %(post.author.name,points))
                else:
                    logging.debug("No commands found in comment")

                #mark_post_alreadydone(pid,cur)
            else:
                continue
                # This comment has already been checked. Skipping.
                #logging.debug("This comment has already been checked. Skipping.")
        else:
            logging.debug("This user/post was deleted: User is '[DELETED]'")
            mark_post_alreadydone(pid,cur)
        placeholder_comment = pid
    return placeholder_comment

def mark_post_alreadydone(pid,cur):
    logging.debug("Setting comment/post as done")
    cur.execute("INSERT INTO alreadydone VALUES(?)", (pid,))
    return

def check_alreadydone(pid,cur):
    cur.execute("SELECT * FROM alreadydone WHERE THREADID=?", (pid,))
    if not cur.fetchone():
        return False
    else:
        return True

# Try to get the author name
def get_author(post):
    try:
        pauthor = post.author.name
    except AttributeError:
        logging.debug("Found deleted author.")
        pauthor = '[DELETED]'
    return pauthor

def get_points(uname,cur):
    logging.debug("Check the points balance for user: %s" %(uname))
    cur.execute("SELECT * FROM points WHERE NAME = ?", (uname,))
    rows = cur.fetchone()
    if rows:
        if rows[0]:
            return rows[0]
    else:
        return False

def set_points(uname,amount,cur):
    logging.debug("Setting %s points for user: %s" %(amount, uname))
    cur.execute("UPDATE points SET AMOUNT = AMOUNT ? WHERE NAME = ?", (uname,amount))
    return

def insert_user(uname,cur):
    logging.debug("This is a new user. Setting their points to 0 for this submissions.")
    cur.execute('INSERT INTO points VALUES(?, ?)', (0, uname))

    return


