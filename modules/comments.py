# encoding: UTF-8

# Comments #
############

# Import #
##########

import re
import logging
import messages
from pprint import pprint
import time
#import database

# Variables #
#############

history = []

# Functions #
#############

# Starts the comments module
def start(data,msg,r):
    logging.debug("Starting Module: Comments")
    subreddit = get_sub(r,data["running_subreddit"]) # gets subreddit object
    sub_comments = sub_get_comments(subreddit) # gets x comments from sub
    process_comments(data,msg,r,sub_comments) # processes the comments

# Gets subreddit object from reddit
def get_sub(r,sub_name):
    logging.debug("Getting Subreddit")
    logging.info("Running in %s" % sub_name)
    return r.get_subreddit(sub_name)

# Gets the newest comments from the subreddit
def sub_get_comments(subreddit):
    logging.debug("Getting Comments")
    return subreddit.get_comments(limit=None) # Limits comments retrieved

# Comment Processing
def process_comments(data,msg,r,sub_comments):
    logging.debug("Processing Comments")
    running_username = str(data["running_username"]).lower()
    for comment in sub_comments: # for each comment in batch
        # If we haven't processed this, or the comment HAS been edited (recheck the message when edited).
        if comment not in history or comment.edited:
            # Track that we've already processed this comment.
            history.append(comment)
            logging.debug("Comment History Count: " + str(len(history)))
            if not comment.banned_by: # Ignores removed comments
                comment_author = str(comment.author.name).lower()
                if comment_author != running_username: # Ignore my own comments
                    logging.info("Searching comment by: %s\n%s" % (comment.author.name
                        if comment.author else "[deleted]",comment.permalink)) # Shows redditor and permalink
                    lines = split_comment(comment.body) # Gets comment lines
                    token_found = search_line(data["token"],lines) # Checks for match
                    if token_found: # Starts checks when a token is found
                        logging.info("Token Found")
                        start_checks(data,msg,r,comment,token_found)
                    else:
                        logging.info("No Token Found")
                else:
                    logging.debug("Comment found was my own.")
                if comment_author == str(comment.submission.author).lower():
                    print("Placeholder: Change Submission Flair")
            else:
                logging.debug("This comment was removed by a mod and has not been scanned.")
        if len(history) > 2000:
            del history[0]

# Starts Checks
def start_checks(data,msg,r,token_comment,token_found):
    logging.debug("Starting Checks")
    # Get bot username and make it lowercase.
    running_username = str(data["running_username"]).lower()
    reviewer = str(token_comment.author.name).lower()
    reviewee_comment = r.get_info(thing_id=token_comment.parent_id)
    if reviewee_comment.author:
        reviewee= str(reviewee_comment.author.name).lower()
        if reviewee == running_username: # Prevents reply to bot
            logging.info("User replied to me")
        elif reviewee == reviewer: # Prevents reply to self
            logging.info("User replied to self")
        elif check_already_replied(data,msg["confirmation"],token_comment.replies,running_username):
            logging.info("Already Confirmed")
        elif check_already_replied(data,msg["error_length"],token_comment.replies,running_username):
            if token_comment.edited:
                optional_checks(data,msg,r,token_comment,reviewer,reviewee_comment,reviewee,token_found)
            else:
                logging.info("Already Notified - Too Short")
        elif check_already_replied(data,msg["error_bad_recipient"],token_comment.replies,running_username):
            logging.info("Already Notified - Bad Recipient")
        elif check_already_replied(data,msg["error_submission_history"],token_comment.replies,running_username):
            logging.info("Already Notified - Submission History Error")
        else:
            optional_checks(data,msg,r,token_comment,reviewer,reviewee_comment,reviewee,token_found)
    else:
        logging.info("Unable to award point to deleted comment")

# Splits comments into lines for more thorough processing
def split_comment(body):
    logging.debug("Splitting Comment Body")
    return body.split("\n") # Splits double line breaks

# Search comment for symbol token
def search_line(data_token,lines):
    logging.debug("Searching Line For Token")
    for line in lines:
        if re.match("(    |&gt;)",line) is None: # Don't look in code or quotes
            for token in data_token: # Check each type of token
                if token in line:
                    return token

# Check to make sure I haven't already replied
def check_already_replied(data,msg,replies,running_username):
    logging.debug("Checking Already Replied")
    for reply in replies:
        try:
            if str(reply.author.name).lower() == running_username:
                if str(msg).lower()[0:10] in str(reply.body).lower():
                    return True
        except:
            logging.debug("Check Failed")


# Optional checks based on configuration
def optional_checks(data,msg,r,token_comment,reviewer,reviewee_comment,reviewee,token_found):
    logging.debug("Optional Checks")
    if check_reviewee_not_author(data["check_ana"],token_comment.submission.author,reviewee):
        error_bad_recipient = messages.error_bad_recipient(data,msg,token_comment)
        token_comment.reply(error_bad_recipient).distinguish()
        logging.info("Error Bad Recipient Sent")
    elif check_reviewer_to_reviewee_history(data,msg,r,reviewee_comment,reviewee,token_comment,reviewer):
        error_submission_history = messages.error_submission_history(msg,reviewee_comment.author.name)
        token_comment.reply(error_submission_history).distinguish()
        logging.info("Error Submission History Sent")
    elif check_length(data,token_comment.body,token_found):
        error_length = messages.error_length(data,msg,reviewee_comment.author.name)
        token_comment.reply(error_length).distinguish()
        logging.info("Error Length Sent")
    else:
        logging.debug("Token Valid - Beginning point Process")
        flair_count = point.start_increment(data,msg,r,reviewee)
        logging.debug("Point Awarded")
        token_comment.save()
        logging.debug("Comment Saved")
        edited_reply = False
        for reply in token_comment.replies:
            if reply.author:
                logging.debug("Editing existing comment")
                if str(reply.author.name).lower() == data["running_username"].lower():
                    confirmation = messages.confirm(data,msg,reviewee_comment,reviewee)
                    reply.edit(confirmation).distinguish()
                    edited_reply = True
        if edited_reply == False:
            logging.debug("Leaving new comment")
            confirmation = messages.confirm(data,msg,reviewee_comment,reviewee)
            token_comment.reply(confirmation).distinguish()
        logging.info("Confirmation Message Sent")
        wait()

def wait():
    wait_time = 35
    logging.debug("Sleeping for %s seconds to clear cache" % wait_time)
    time.sleep(wait_time)

# Check to ensure submission author is not receiving a token
def check_reviewee_not_author(check_ana,sub_author,reviewee):
    if check_ana == "1":
        logging.debug("Checking reviewee Not Author")
        return str(sub_author).lower() == str(reviewee).lower()
    elif check_ana == "0":
        logging.debug("Check Recipient Not Author is disabled.")

# Checks to see if the reviewer has already reviewed the reviewee in this thread
def check_reviewer_to_reviewee_history(data,msg,r,reviewee_comment,reviewee,token_comment,reviewer):
    if data["check_history"] == "1":
        # TREE means it will only search the root comment and all replies
        logging.debug("Checking reviewer to reviewee History - TREE")
        root = reviewee_comment
        while not root.is_root: # Move to the top comment
            root = r.get_info(thing_id=root.parent_id)
        if iterate_replies(data,msg,r,root,reviewee,reviewer):
            logging.info("Point awarded already for this reviewer in this thread")
            return True
    elif data["check_history"] == "0":
        logging.debug("Check reviewer to reviewee History is disabled.")

# Iterates through the comment tree - VERY expensive
def iterate_replies(data,msg,r,comment,reviewee,reviewer):
    logging.debug("Iterating Replies")
    iterate = "Yes"
    msg_confirmation = msg["confirmation"]
    running_username = str(data["running_username"]).lower()
    try:
        comments = r.get_submission(comment.permalink).comments
    except:
        return iterate
    for comment in comments:
        if iterate == "Yes":
            if check_already_replied(data,msg_confirmation,comment.replies,running_username):
                if check_reviewer(r,comment,reviewer):
                    if check_reviewee(r,comment,reviewee):
                        iterate = "No"
                        return iterate
            for reply in comment.replies:
                iterate = iterate_replies(data,msg,r,reply,reviewee,reviewer)
                if iterate == "No":
                    return iterate
        elif iterate == "No":
            # Not sure this is ever called
            print("Comment NoIteration Called - Remove this line and comment")
            logging.critical("Comment NoIteration Called - Remove this line and comment")
            return iterate

# Checks original reviewer against recently found reviewer
def check_reviewer(r,comment,orig_reviewer):
    logging.debug("Checking reviewer")
    try:
        reviewer = str(comment.author.name).lower()
    except:
        reviewer = "[deleted]"
    if reviewer == orig_reviewer:
        return True

# Checks original reviewee against recently found reviewee
def check_reviewee(r,comment,orig_reviewee):
    logging.debug("Checking reviewee")
    reviewee_comment = r.get_info(thing_id=comment.parent_id)
    try:
        reviewee = str(reviewee_comment.author.name).lower()
    except:
        reviewee = "[deleted]"
    if reviewee == orig_reviewee:
        return True

# Check length of comment against minimum requirement
def check_length(data,body,token_found):
    if data["check_length"] == "1":
        logging.debug("Checking Comment Length")
        if token_found != "force":
            return len(body) < int(data["min_length"]) + len(token_found)
    elif data["check_length"] == "0":
        logging.debug("Check Comment Length is disabled.")

# EOF