# encoding: utf-8

# Point #
############

# Import #
##########

import praw
import logging
import re
import messages


# Functions #
#############

def start_increment(data,msg,r,reviewee):
  logging.debug("Starting Module: Point - Increment")
  # The text in the flare from a thread where you want to subtract 2 points from the author.
  # It removes the post if the author has less than 2 points.
  flairs_to_subtract = ("Review Video", "Channel Critique")
  current_flair = get_flair(data,msg,r,reviewee)
  print current_flair

  return

def start_decrement(data,msg,r,reviewee):
  logging.debug("Starting Module: Token - Decrement")
  current_flair = get_flair(data,msg,r,reviewee)

  return

def get_flair(data,msg,r,reviewee):
  logging.debug("Getting the awardee's flair")
  reviewee_flair = r.get_flair(data["running_subreddit"], reviewee)
  return reviewee_flair


#def set_flair(data,msg,r,reviewee,reviewee_flair):
#  logging.debug("Setting the reviewee's new flair")
#  r.set_flair(data["running_subreddit"],reviewee,reviewee_flair["flair_text"])

# EOF

