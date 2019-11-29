import sqlite3

class Database():
    def __init__(self):
        self.createEntryTable = """
            CREATE TABLE IF NOT EXISTS entries (
                id integer PRIMARY KEY,
                date text NOT NULL,
                name text NULL
            )
        """

        self.createLogsTable = """
            CREATE TABLE IF NOT EXISTS logs (
                id integer PRIMARY KEY,
                millis integer NOT NULL,
                entryId integer NOT NULL,        
                side text NOT NULL,
                vecW real NOT NULL,
                vecX real NOT NULL,
                vecY real NOT NULL,
                vecZ real NOT NULL,
                FOREIGN KEY (entryId) REFERENCES entries (id)
            )
        """

        self.insertEntry = """
            INSERT INTO entries(date, name)
            VALUES(?, ?) 
        """

        self.insertLog = """
            INSERT INTO logs(millis, entryId, side, vecW, vecX, vecY, vecZ)
            VALUES(?,?,?,?,?,?,?) 
        """
    
    def setupSchema(self, dbFile):        
        try:
            self.conn = sqlite3.connect(dbFile)
            self.conn.execute(self.createEntryTable)
            self.conn.execute(self.createLogsTable)
        except Exception as e:
            print(e)
    
    def createNewEntry(self, date):
        try:
            cur = self.conn.cursor()
            cur.execute(self.insertEntry, date)
            self.conn.commit()
            return cur.lastrowid
        except Exception as e:
            print(e)
    
    def createNewLog(self, log):        
        try:
            cur = self.conn.cursor()
            cur.execute(self.insertLog, log)
            self.conn.commit()
            return cur.lastrowid
        except Exception as e:
            print(e)
    
    def getLogsFromEntry(self, entryId):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM logs WHERE entryId=?", (entryId,))            
            return cur.fetchall()
        except Exception as e:
            print(e)    
    
    def getAllEntries(self):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM entries")
            return cur.fetchall()
        except Exception as e:
            print(e)
    
    def getLastEntry(self):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT MAX(Id) FROM entries")
            return cur.fetchall()[0][0]
        except Exception as e:
            print(e)
            return 0