import sqlite3

def start(database):
    sql = sqlite3.connect(database)
    print "Loaded SQL Database"
    cur = init_db(sql)
    sql.commit()
    sql.close()

def init_db(sql):
    cur = sql.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS points(AMOUNT NAME)")
    cur.execute("CREATE TABLE IF NOT EXISTS alreadydone(THREADID)")
    print "Loaded SQL tables"
    sql.commit()
    return cur

def insert_user(cur, name):
    cur.execute("INSERT INTO points VALUES(?,?)",(1,name))
    print "Point awarded successfully in database for user: %s." % name
    return

def update_user(cur, amount, user):
    cur.execute("UPDATE points SET AMOUNT = AMOUNT %s WHERE NAME = ?", (user,))

    print "Point awarded to existing user: %s." % user
    return

def select_user(cur, user):
    cur.execute("SELECT * FROM points WHERE NAME=?", (user,))
    return

