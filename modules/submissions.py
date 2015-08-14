# encoding: UTF-8


# Import #
##########

import praw
import re
import logging
import time
from pprint import pprint

# Functions #
#############

# Start the Submission module
def start(data,msg,r,cur,placeholder_submission):
    logging.debug("Starting Module: Submissions")
    # Get the subreddit object)
    subreddit = get_sub(r,data["settings"]["subreddit"])
    #if placeholder_submission:
    #    posts = sub_get_submissions(subreddit, placeholder_submission)
    #else:
    #    posts = sub_get_submissions(subreddit)
    #posts = sub_get_submissions(subreddit)
    #for post in posts:
    #    dir(post)
    posts = subreddit.get_new(limit = 100)
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
    #if placeholder_submission:
    #    return subreddit.get_new(placeholder = placeholder_submission)
    #else:
    return subreddit.get_new(limit=100) # Limits submissions retrieved

# Process post comments
def process_comments(data,msg,r,post,flat_comments,cur):
    logging.debug("Processing comments of post.")
    for comment in flat_comments:
        cauthor = get_author(comment)
        pauthor = get_author(post)
        users_commented = comment_set(comment.id,post.id,cauthor,cur,"SELECT")
        # Ignore comments made on own thread, except commands which have already been processed.
        if pauthor == cauthor:
            # They commented on their own post. Ignoring.
            #logging.debug("User (%s) commented on their own post. (Post author: %s). Ignoring comment." %(cauthor,pauthor))
            comment_set(comment.id,post.id,cauthor,cur,"INSERT",1)
            continue
        if cauthor not in data['ignore']['users']:
            # Check the database to see if anyone has posted to this post already.
            if not users_commented:
                # No users have commented on this thread.
                # Make sure it meets the comment length for a review
                if len(comment.body) >= 50:
                    points = get_points(cauthor,cur)
                    # Set the points to 0 if the value is "None"
                    if points == None:
                        points = 0
                    # If the points are greater than or equal to 0
                    if points >= 0:
                        # Set the comment as marks done.
                        comment_set(comment.id,post.id,cauthor,cur,"INSERT",1)
                        # Add 1 point to the users account
                        add_points(cauthor,cur)
                    else:
                        # New user found. Add them to the database with a new point.
                        insert_user(cauthor,cur)
                        logging.debug("Adding point to new user")
                        add_points(cauthor,cur)
                        # Mark the comment and done.
                        comment_set(comment.id,post.id,cauthor,cur,"INSERT",1)
                else:
                    if cauthor != data['settings']['username']:
                        logging.debug("Comment made by %s did not meet the required minimum 50 words for review" %(cauthor))
                        comment.reply("You're comment did not meet the required minimum 50 words for review. No points added to account. Please edit your review to receive the points in your account. NOTE: THIS FEATURE MAY HAVE ISSUES RIGHT NOW")
                        comment_set(comment.id,post.id,cauthor,cur,"INSERT")
            else:
                # Figure out if this comment author has already been put into the database for this post.
                for user in users_commented:
                    # If the user is in the database
                    if cauthor == user[1]:
                        # If the user has points skip the user
                        if user[2] > 0:
                            # Skipping. User already assigned points for this post.
                            #logging.debug("Skipping user. They've already received points for this post.")
                            pass
                        else:
                            # This is likely an edited comment or it never got marked as done since it didnt have at least 50 words.
                            # If the comment greater than or equal to 50 words.
                            if check_length:
                                # Add 1 point to users account
                                add_points(cauthor,cur)
                                # mark the comment as completed by giving them 1 point for this thread.
                                comment_set(comment.id,post.id,cauthor,cur,"UPDATE",1)
                            else:
                                logging.debug("Rechecked comment, but it still didn't meet the 50 character minimum")
                                # If the user did not meet the requirements and its not the bots comment. Inform them.
                                if cauthor != data['settings']['username']:
                                    #comment.reply("You're commented did not meet the required minimum 50 words for review. No points added to account. Please edit your review to receive the points in your account")
                                    logging.debug("COMMENTING TO THE USER")
                                logging.debug("Comment made by %s did not meet the 50 word minimum." %(cauthor))
                                comment_set(comment.id,post.id,cauthor,cur,"INSERT")
                                pass
                    else:
                        pass

        else:
            #logging.debug('Skipping this user. They are on the ignore list')
            pass
    return

def check_length(message):
    if len(message.body) >=50:
        return True

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
                if post.link_flair_text in data["flair"]["subtract"]:
                    # Process the comments for the post.
                    flat_comments = praw.helpers.flatten_tree(post.comments)
                    process_comments(data,msg,r,post,flat_comments,cur)
                # Check to see if the flair_text exists in the flair to subtract points.
                post_status = check_alreadydone(post.id,cur)
                if not post_status and post.link_flair_text in data["flair"]["subtract"]:
                    logging.debug("Found a post not in history, and has Flair.")
                    uname = pauthor
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
                                #logging.debug("I WOULD NORMALLY REMOVE THIS POST")
                                r.send_message(uname, "Not enough points to submit to %s" %(data['settings']['subreddit']), msg['error_more_points'] %(points))
                                result = post.remove()
                                if result == None:
                                    logging.debug("Failed to remove submission")
                                mark_post_alreadydone(post.id,cur)
                            else:
                                # This user exists in the database so go ahead and subtract the 2 points for this post.
                                remove_points(uname,cur)
                                # Add this post to the database history as alreadydone
                                mark_post_alreadydone(post.id,cur)
                        else: # If a user has no points, then they are not in the database.
                            logging.debug("User not found in database. Adding user with 0 points.")
                            insert_user(uname,cur)
                    else:
                        logging.debug("This user is on the Ignore list")
                elif post_status and post.link_flair_text in data["flair"]["subtract"]:
                    # If this post has already been marked as "Done" recheck the comments to make sure nothing new is here.
                    flat_comments = praw.helpers.flatten_tree(post.comments)
                    for comment in flat_comments:
                        if comment.edited: # If a comment was edited, reprocess the comment.
                            process_comments(data,msg,r,post,flat_comments,cur)
                        else:
                            # If the comment was not edited, skip it.
                            pass
                else:
                    # Does not contain flair text to subtract from.
                    pass
        else:
            logging.debug("This user/post was deleted: User is '[DELETED]'")

        mark_post_alreadydone(post.id,cur)
        placeholder_submission = pid
    return placeholder_submission

def mark_post_alreadydone(pid,cur):
    cur.execute("INSERT OR IGNORE INTO alreadydone VALUES(?)", (pid,))
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
        insert_user(uname,cur)
        cur.execute("SELECT * FROM points WHERE NAME = ?", (uname,))
        rows = cur.fetchone()
        if rows:
            if rows[0]:
                return rows[0]
        else:
            return False

def remove_points(uname,cur):
    logging.debug("Removing 2 points for user: %s" %(uname))
    cur.execute("UPDATE points SET AMOUNT = AMOUNT - 2 WHERE NAME = ?", (uname,))
    return

def add_points(uname,cur):
    logging.debug("Adding 1 point for user: %s" %(uname))
    cur.execute("""UPDATE points SET AMOUNT = AMOUNT + 1 WHERE NAME = ?""", (uname,))
    return

def insert_user(uname,cur):
    logging.debug("This is a new user. Setting their points to 0 for this submissions.")
    cur.execute('INSERT OR IGNORE INTO points VALUES(?, ?)', (0, uname))
    return

def comment_set(comment_id,post_id,uname,cur,action=None,points=None):
    if action == "UPDATE":
        cur.execute("""UPDATE comments SET POINTS_ADDED = 1 WHERE THREADID = ? AND NAME=? AND SUBMISSION_ID = ?""", (comment_id,uname,post_id))
        return
    elif action == "INSERT":
        cur.execute('INSERT OR IGNORE INTO comments VALUES(?, ?, ?, ?)', (comment_id, uname, points, post_id))
        return
    elif action == "SELECT":
        cur.execute('SELECT * FROM comments WHERE SUBMISSION_ID = ? AND NAME=?', (post_id, uname))
        rows = cur.fetchall()
        return rows
    return

def get_users_commented(post_id,uname,cur):
    cur.execute('SELECT * FROM comments WHERE SUBMISSION_ID = ? AND NAME=?', (post_id, uname))
    rows = cur.fetchall()
    if rows:
        return rows
    else:
        return False


