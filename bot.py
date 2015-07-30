# Reddit bot made with praw for /u/TroaAxaltion, made by /u/bmheight
# Made with Python 3.4
# Usage: say "GetScore! "username"" to get the score from an user, comment on a post with "✓" to award a point to that user. It removes posts with a flair in the flairs_to_subtract tuple if they have less than 2 points.
import praw
import time
import sqlite3
import re

class Bot(object):
    def __init__(self):
        self.__version__ = "1.5"
        # The name of the database. It will be created in the same directory
        self.database = "r_youtubers.db"
        self.reddit_username = ""
        self.password = ""
        # Short description.
        self.useragent = "Point system, owner: /u/TroaAxaltion, developer: /u/bmheight, version: {}".format(self.__version__)
        # The text in the flare from a thread where you want to subtract 2 points from the author.
        # It removes the post if the author has less than 2 points.
        self.flairs_to_subtract = ("Review Video", "Channel Critique")
        # Everyone in this tuple is ignored in the point system and posts from these usernames aren't removed.
        self.ignore_list = ("TroaAxaltion", "twinsofliberty", "Lunatic14", "desenagrator", "InstantKevin", "DannyLunch", "DlmaoC", "RazorINC", "SpinalColumnA", "pollichops")
        # Initialize the r variable and set to Null.
        self.r = None
        # Connect to/create the database file
        self.sql = sqlite3.connect(self.database)
        print("Loaded SQL database")
        self.cur = self.sql.cursor()
        # Initialize the Database tables.
        self.init_db()
        self.reddit_login()

    def init_db(self):
        self.cur.execute('CREATE TABLE IF NOT EXISTS points(AMOUNT NAME)')
        self.cur.execute('CREATE TABLE IF NOT EXISTS alreadydone(THREADID)')
        print("Loaded SQL tables")
        self.db_commit()
        return

    def db_commit(self):
        self.sql.commit()
        return

    def db_close(self):
        self.sql.close()
        return

    def reddit_login(self):
        self.r = praw.Reddit(self.useragent)
        self.r.login(self.reddit_username, self.reddit_password)
        return

    def scan_sub(self, placeholder_submission, placeholder_comment):
        print("Searching " + self.subreddit +".")
        sr = self.r.get_subreddit(self.subreddit)
        if placeholder_comment:
            posts = sr.get_comments(placeholder = placeholder_comment)
        else:
            posts = sr.get_comments(limit = 20)
        for post in posts:
            pid = post.id
            try:
                pauthor = post.author.name
            except AttributeError:
                pauthor = "[DELETED]"
            plink = post.permalink
            print("Scanning id: " + pid)
            pbody = post.body.lower()
            comment = None
            if "getscore! " in pbody:
                print("Found " + pid + " by " + pauthor)
                uname = re.findall(r'getscore!\s"+(.*)"+', pbody)[0]
                self.cur.execute('SELECT * FROM points WHERE NAME=?', (uname,))
                if uname in ignore_list:
                    print("Someone tried GetScore! on someone in the ignore list")
                    post.reply("{} is ignore in the point system.".format(uname))
                elif cur.fetchone():
                    print("Replying with " + self.cur.fetchone()[0])
                    post.reply("{} has a score of {}.".format(uname self.cur.fetchone()[0]))
                    print("Permalink: " + plink)
                else:
                    print("Can't reply the score since " + uname + " doesn't have a score yet")
                    post.reply("{} doesn't have a score yet.".format(uname,))
            elif "✓" in pbody and pauthor == comment.submission.author and comment.submission.link_flair_text in flairs_to_subtract:
                print('Found ' + pid + ' by ' + pauthor)
                parent_name = post.parent_id.author
                self.cur.execute('SELECT * FROM points WHERE NAME=?', (parent_name,))
                if pauthor in ignore_list:
                    post.reply("{} is ignored in the point system.".format(uname))
                elif cur.fetchone():
                    self.cur.execute("UPDATE points SET AMOUNT = AMOUNT + 1 WHERE NAME = ?", (parent_name,))
                    post.reply("Point awarded to {}.".format(parent_name))
                else:
                    self.cur.execute('INSERT INTO points VALUES(?, ?)', (1, parent_name))
                    post.reply("Point awarded to {}.".format(parent_name))
            placeholder_comment = pid
        if placeholder_submission:
            threads = sr.get_new(placeholder = placeholder_submission)
        else:
            threads = sr.get_new(limit = 15)
        for thread in threads:
            self.cur.execute("SELECT * FROM alreadydone WHERE THREADID=?", (thread.id,))
            if thread.author in ignore_list:
                continue
            elif thread.link_flair_text in flairs_to_subtract and not self.cur.fetchone():
                self.cur.execute("SELECT * FROM points WHERE NAME=?", (thread.author.name,))
                if not self.cur.fetchone():
                    self.cur.execute('INSERT INTO points VALUES(?, ?)', (2, thread.author.name))
                self.cur.execute("SELECT * FROM points WHERE NAME=?", (thread.author.name,))
                if self.cur.fetchone()[0] < 2:
                    thread.add_comment("You don't have enough points to do this.")
                    thread.remove()
                    print("Removed thread id " + thread.id + " because the author didn't have enough points")
                    self.cur.execute("INSERT INTO alreadydone VALUES(?)", (thread.id,))
                else:
                    self.cur.execute("INSERT INTO alreadydone VALUES(?)", (thread.id,))
                    self.cur.execute("UPDATE points SET AMOUNT = AMOUNT - 2 WHERE NAME = ?", (thread.author.name,))
            placeholder_submission = thread.id
        self.db_commit()
        self.db_close()
        return placeholder_submission, placeholder_comment

if __name__ == "__main__":
    # The time it sleeps after scanning the last 15 posts before scanning again in seconds. Default: 300
    time_to_sleep = 300
    placeholder_submission = None
    placeholder_comment = None
    bot = Bot()
    while True:
        try:
            placeholder_submission, placeholder_comment = bot.scan_sub(placeholder_submission, placeholder_comment)
        except Exception as e:
            print("An error occurs: " + str(e))
        print ("Sleeping for {} seconds.".format(time_to_sleep))
        time.sleep(time_to_sleep)
