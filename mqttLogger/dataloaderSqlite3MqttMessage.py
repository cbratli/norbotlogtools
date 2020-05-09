import sqlite3
import time
import datetime

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates



class Dataloader(object):
    screenX = 1000
    screenY = 1000
    scale = 0.1
    index = 1
    
    
    def __init__(self, filename):
        conn = sqlite3.connect(filename)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        IdToUse = 1
        self.measurements = []
        self.datasetCounter = 0

        import MessageTypeMqtt        
        sql = MessageTypeMqtt.MessageTypeMqtt.sqlSelectAll
        IdToUse = 1
        dataCursorFromDatabase = c.execute(sql, [(IdToUse)])
        self.messages = []
        for row in dataCursorFromDatabase:
            data = {}
            data['localDateTime'] = row['localDateTime']
            data['localUnixTime'] = row['localUnixTime']
            data['msgToTopic'] = row['msgToTopic']
            data['message'] = row['message']
            self.messages.append(data)            
        c.close()
        conn.close()
             

    def getData(self):
        self.datasetCounter = (self.datasetCounter + 1) % len(self.messages)
        return self.messages[self.datasetCounter]

    def getDataLength(self):
        return len(self.messages)

