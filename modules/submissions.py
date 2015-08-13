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

# Start the Submission module
def start(data,msg,r,cur,placeholder_submission):
    logging.debug("Starting Module: Submissions")
    # Get the subreddit object)
    subreddit = get_sub(r,data["settings"]["subreddit"])
    if placeholder_submission:
        posts = sub_get_submissions(subreddit, placeholder_submission)
    else:
        posts = sub_get_submissions(subreddit)
    process(data,msg,r,posts,cur,placeholder_submission)
    return placeholder_submission

# Gets the subreddit object from reddit
def get_sub(r,sub_name):
    logging.debug("Getting Subreddit")
    logging.info("Running in %s" % sub_name)
    return r.get_subreddit(sub_name)

# Gets the newest submissions from the subreddit
def sub_get_submissions(subreddit, placeholder_submission = None):
    logging.debug("Getting Submissions")
    if placeholder_submission:
        return subreddit.get_new(placeholder = placeholder_submission)
    else:
        return subreddit.get_new(limit=20) # Limits submissions retrieved

# Processes the posts
def process(data,msg,r,posts,cur,placeholder_submission):
    logging.debug("Processing Post Submissions")
    bot_name = str(data["settings"]["username"]).lower()
    for post in posts:
        pid = post.id
        pauthor = get_author(post)
        if pauthor != "[DELETED]":
            # Check to make sure the link_flair_text exists, otherwise we'll error out.
            if post.link_flair_text:
                # Check to see if the flair_text exists in the flair to subtract points.
                logging.debug("Checking Flair for post.")
                post_status = check_alreadydone(post.id,cur)
                if not post_status and post.link_flair_text in data["flair"]["subtract"]:
                    logging.debug("Found a post not in history, and has Flair.")
                    uname = post.author.name
                    # The post is not in our history and contains the text "Review Video", or "Channel Critique"
                    if uname not in data["ignore"]["users"]:
                        logging.debug("Checking users points")
                        points = get_points(uname,cur)
                        if points == None:
                            points = 0
                        # Make sure points != False
                        if points >=0 :
                            # Make sure the user has at least 2 points to post this thread.
                            if points < 2:
                                logging.debug("User: %s does not have enough points to do this." %(uname))
                                #post.add_comment("You do not have enough points to do this.")
                                mark_post_alreadydone(post.id,cur)
                            else:
                                logging.info("Subtracting 2 points from %s account balance" %(uname))
                                # This user exists in the database so go ahead and subtract the 2 points for this post.
                                set_points(uname,-2)
                                # Add this post to the database history as alreadydone
                                mark_post_alreadydone(post.id,cur)
                        else: # If a user has no points, then they are not in the database.
                            logging.debug("User not found in database. Adding user with 0 points.")
                            insert_user(uname,cur)
                            mark_post_alreadydone(post.id,cur)
                    else:
                        logging.debug("This user is on the Ignore list")
                        # Mark posts made by the people on the ignore list as done so we skip them in the future
                        mark_post_alreadydone(post.id,cur)
                else:
                    # Does not contain flair text to subtract from.
                    continue
        else:
            logging.debug("This user/post was deleted: User is '[DELETED]'")

        placeholder_submission = pid

def mark_post_alreadydone(pid,cur):
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


