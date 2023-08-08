import mysql.connector
import datetime
from Config import config
from zoneinfo import ZoneInfo


# Adding user to the database

async def add_user(chat_id, name, username):
    mydb.connect()
    time = datetime.datetime.now(tz=ZoneInfo("Asia/Tehran"))
    sql = "INSERT IGNORE INTO users (ID,Name,Username,Created) VALUES (%s,%s,%s,%s)"
    val = (chat_id, name, username, time)
    mycursor.execute(sql, val)
    mydb.commit()
    sql = "INSERT IGNORE INTO settings (ID) VALUES (%s)"
    val = (chat_id,)
    mycursor.execute(sql, val)
    mydb.commit()
    mydb.close()


# adding user process


async def add_last_processing(userid):
    mydb.connect()
    time = datetime.datetime.now()
    sql = 'UPDATE users SET Last_Processing=%s WHERE ID=%s'
    val = (time, userid)
    mycursor.execute(sql, val)
    mydb.commit()
    mydb.close()


# read user last process
async def read_last_processing(userid):
    mydb.connect()
    time = datetime.datetime.now(tz=ZoneInfo("Asia/Tehran"))
    sql = 'SELECT Last_Processing FROM users WHERE ID="%s"'
    val = (userid,)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()[0]
    mydb.close()
    return result, time


# read all users
async def all_users(count=True):
    mydb.connect()
    if count:
        sql = 'SELECT COUNT(ID) FROM users'
        mycursor.execute(sql)
        result = mycursor.fetchone()[0]
    else:
        sql = 'SELECT ID FROM users'
        mycursor.execute(sql)
        result = mycursor.fetchall()
    mydb.close()
    return result


# adding user step
async def set_step(chat_id, step):
    mydb.connect()
    sql = "UPDATE users SET Step=%s WHERE ID=%s"
    val = (step, chat_id)
    mycursor.execute(sql, val)
    mydb.commit()
    mydb.close()


# reading user step
async def get_step(chat_id):
    mydb.connect()
    sql = 'SELECT Step FROM users WHERE ID=%s'
    val = (chat_id,)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()[0]
    mydb.close()
    return result


# adding enhance type
async def set_type(chat_id, type_):
    mydb.connect()
    sql = "UPDATE settings SET Type=%s WHERE ID=%s"
    val = (type_, chat_id)
    mycursor.execute(sql, val)
    mydb.commit()
    mydb.close()


# reading enhance type
async def get_type(chat_id):
    mydb.connect()
    sql = 'SELECT Type FROM settings WHERE ID=%s'
    val = (chat_id,)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()[0]
    mydb.close()
    return result


# connecting to database

mydb = mysql.connector.connect(
    host=config.host,
    user=config.user,
    password=config.password,
    database=config.database
)

mycursor = mydb.cursor()

mydb.close()
