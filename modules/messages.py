# Messages #
############

# Import

import praw
import yaml
import logging
import time

# Functions

# Reads in the yml for the messages
def read_msg_yaml(yml_file):
    with open(yml_file, 'r') as ymlfile:
        msg = yaml.load(ymlfile)
    return msg

