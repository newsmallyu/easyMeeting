# -*- coding: utf-8 -*-
#!usr/bin/python3
# ubuntu16.04LTS

import sqlite3
import time

def connectDatabase():
    conn = sqlite3.connect("C:/Users/ay05/PycharmProjects/easyMeeting/cgi/easymeeting.db")
    return (conn, conn.cursor())

"""
用户注册、登录等相关
"""
def createUserTable():
    conn, cursor = connectDatabase()

    # get all table name in database
    cursor.execute("SELECT NAME FROM sqlite_master WHERE TYPE='table'")
    table_list = [name[0] for name in cursor.fetchall()]

    if not 'users' in table_list:
        cursor.execute("""CREATE TABLE users
                 (NAME TEXT PRIMARY KEY NOT NULL,
                  PASSWORD TEXT NOT NULL);""")
    return (conn, cursor)


def createUser(name, pwd, repeate_pwd):
    # 如果users不存在则首先创建表users
    conn, cursor = createUserTable()

    # TODO: 用户名格式和密码格式校验, 密码重复验证
    # TODO: 密码的加密处理
    # 检查name是否存在，不存在才能插入值
    cursor.execute("SELECT NAME FROM users WHERE NAME='{}'".format(name))
    if (not cursor.fetchall()):
        cursor.execute("""INSERT INTO users (NAME, PASSWORD)
                       VALUES ('{}', '{}')""".format(name, pwd))
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE NAME='{}'".format(name))
        user = cursor.fetchone()
        conn.close()
        # s_: 表示已经加密处理
        return {'name': user[0], 's_password': user[1]}

def loginUser(name, pwd):
    conn, cursor = connectDatabase()
    cursor.execute("SELECT * FROM users WHERE NAME='{}'".format(name))
    query_user = cursor.fetchone()
    if query_user:
        if (name == query_user[0] and pwd == query_user[1]):
            return {'name': query_user[0], 's_password': query_user[1]}


"""
预定会议相关
"""
def createMeetingTable():
    conn, cursor = connectDatabase()

    # query all tables name in database
    cursor.execute("SELECT NAME FROM sqlite_master WHERE TYPE='table'")
    table_list = [name[0] for name in cursor.fetchall()]

    if not "meetings" in table_list:
        cursor.execute("""CREATE TABLE meetings
                        (ID INT PRIMARY KEY NOT NULL,
                         TIMESTAMP TEXT NOT NULL,
                         TITLE TEXT NOT NULL,
                         ROOM TEXT NOT NULL,
                         START TEXT NOT NULL,
                         END TEXT NOT NULL,
                         USER_NAME TEXT NOT NULL);""")
    return (conn, cursor)

def dateSplit(dateStr):
    date = dateStr.split(":")
    return int(date[0]+date[1])


def get_totalcell(user):
    conn, cursor = createMeetingTable()
    cursor.execute("""SELECT * FROM meetings
                WHERE USER_NAME ='{}'""".format(user))
    meetingcount = len(cursor.fetchall())
    return meetingcount

def addMeeting(timestamp, title, room, start, end, user_name):
    id = int(time.time() * 10000000)
    # 如果meetings不存在则首先创建表meetings
    conn, cursor = createMeetingTable()
    length = 0
    startnum = dateSplit(start)
    endnum = dateSplit(end)
    # 首先查询是否有重复的会议室预定数据，无则增加，否则返回None
    cursor.execute(""" SELECT * FROM meetings
            WHERE TIMESTAMP='{}' and
                  ROOM='{}' """.format(timestamp, room))
    meetings = cursor.fetchall()
    for i in meetings:
        if dateSplit(i[4]) <= startnum < dateSplit(i[5]) or dateSplit(i[4]) < endnum < dateSplit(i[5]):
            length = length+1
        elif startnum < dateSplit(i[4]):
            if endnum > dateSplit(i[5]) or dateSplit(i[4]) < endnum <= dateSplit(i[5]):
                length = length+1
    if length <= 0:
        cursor.execute("""INSERT INTO meetings (ID, TIMESTAMP, TITLE, ROOM, START, END, USER_NAME)
                       VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}')"""
                              .format(id, timestamp, title, room, start, end, user_name))
        conn.commit()
        cursor.execute("SELECT * FROM meetings WHERE ID={}".format(id))
        meeting = cursor.fetchone()
        conn.close()
        # s_: 表示已经加密处理
        return {
            "id": meeting[0],
            "timestamp": meeting[1],
            "title": meeting[2],
            "room": meeting[3],
            "start": meeting[4],
            "end": meeting[5],
            "user_name": meeting[6]
        }

def queryMeetings(start_timestamp, end_timestamp):
    conn, cursor = createMeetingTable()
    cursor.execute("""SELECT * FROM meetings
            WHERE TIMESTAMP >= {} and
                  TIMESTAMP <= {}""".format(start_timestamp, end_timestamp))
    meetings = cursor.fetchall()
    return meetings

def queryMeetingByUser(user, startnum, page_size):
    conn, cursor = createMeetingTable()
    if(user == "admin"):
        cursor.execute("SELECT * FROM meetings limit '{}' offset '{}'".format(int(page_size), int(startnum)))
    else:
        cursor.execute("""SELECT * FROM meetings
                WHERE USER_NAME ='{}' limit '{}' offset '{}'""".format(user, int(page_size), int(startnum)))
    meetings = cursor.fetchall()
    return meetings

def queryMeetingALL():
    conn, cursor = createMeetingTable()
    cursor.execute("SELECT * FROM meetings")
    meetings = cursor.fetchall()
    return meetings

def deleteMeetingById(id):
    try:
        conn, cursor = createMeetingTable()
        cursor.execute("""DELETE FROM meetings
            WHERE ID={}""".format(id))
        conn.commit()
    except Exception as e:
        raise e
    finally:
        conn.close()
    return "success"

if __name__ == '__main__':
#    print(queryMeetings("1464451200000", "1478966400000"))
#    createMeetingTable()
#    print(queryMeetingByUser())
#    queryMeetingALL()
#    queryMeetingByUser("admin", 1 , 1)
    get_totalcell("admin")
#    deleteMeetingById(15542741082021832)