import sqlite3

class DBAccess:
    def __init__(self,dbfile):
        self.dbfile = dbfile
        self.InitSQLite()

    def __del__(self):
        self.connection.commit()
        self.connection.close()
        self.connection=None
        self.cursor=None
        self.dbfile=None

    def InitSQLite(self):
        self.connection = sqlite3.connect(self.dbfile)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        self.ExecuteSQL('PRAGMA foreign_keys=ON')

    def ExecuteSQL(self,query,parameters=[]):
        self.cursor.execute(query,parameters)
        # return the execution results
        return self.cursor.fetchall()

    def GetLastRowId(self):
        return self.cursor.lastrowid



