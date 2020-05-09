import signal
import time
import sqlite3
import time
import datetime
import sys
import traceback
import threading

class MessageTypeMqtt:
    messages = []
    sqlCmd = """INSERT INTO logMessage (ID, localDateTime, localUnixTime, msgToTopic, message ) VALUES (?,?,?,?,?)"""
    countAllCmd = """Select count(*) from logMessage"""
    nextIdCmd = 'select max(ID)+1 from logMessage'
    sqlSelectAll = "SELECT ID, localDateTime, localUnixTime, msgToTopic, message FROM logMessage WHERE ID=?"
    def __init__(self):
        self.logId = -1
        self.conn = ''
        pass

    def initialize(self, conn, cursor):
        # If we cant select from our table, then create the database.
        self.conn = conn
        try:
            cursor.execute(self.countAllCmd)
            print("logMessage table found")
        except:
            print("Table logMessage not found. Creating table.")
            self.createTable(cursor);
    
        sql = self.nextIdCmd
        result = cursor.execute(sql)
        logIdData = result.fetchone()
        if logIdData[0] == None:
            logId = 1
        else:
            logId = int(logIdData[0])
        self.logId = logId
        print("logId:%d" % logId)
        return logId

    def saveMessage(self,message):

            #sm = messageWithoutType.split(',')
            topic = message[0]
            msg = message[1]
            date = str(datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S'))
            
            logTupple =  (self.logId, date, time.time(), topic, msg)
            self.messages.append(logTupple);

    def writeRecordsToDatabase(self, conn, cursor):
        if len(self.messages) > 0:
            print("Writing %d messages" % len(self.messages))
            #print self.messages[0]
            cursor.executemany(self.sqlCmd,self.messages)
            self.conn.commit()
            self.messages = []

    def createTable(self,c):
        # input: c-Cursor
        
        #ID             - Every time we plot, we get the max(ID)+1 and use that as ID for the logging session.
        #localDateTime  - Datetime on raspberry pi.
        #message- The message we receive
        c.execute("CREATE TABLE logMessage(ID INT, localDateTime TEXT, localUnixTime REAL, msgToTopic TEXT, message TEXT)")
        self.conn.commit()
        
    
if __name__ == '__main__':
    pass
