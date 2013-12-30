import sqlite3
import re
from ScanPath import *

def insensitive_regex_match(expr, item):
    reg = re.compile(expr, re.I)
    return reg.search(item) is not None

def sensitive_regex_match(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None

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
        self.connection.isolation_level = None
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

        self.ExecuteSQLCommand('PRAGMA foreign_keys=ON')
        self.ExecuteSQLCommand('PRAGMA synchronous=NORMAL')
        self.ExecuteSQLCommand('PRAGMA journal_mode=WAL')
        self.ExecuteSQLCommand('PRAGMA ignore_check_constraints=off')

        # regexp matches case sensitive
        self.connection.create_function("REGEXP", 2, sensitive_regex_match)
        # match matches case insensitive
        self.connection.create_function("MATCH", 2, insensitive_regex_match)

    def ExecuteSQLCommand(self,query,parameters=[]):
        self.cursor.execute(query,parameters)
        # return the execution results
        return self.cursor.fetchall()

    def ExecuteSQLScriptFile(self,filename):
        sqlscript=open(filename,'r').read()
        self.ExecuteSQLScript(sqlscript)

    def ExecuteSQLScript(self,sqlscript):
        self.cursor.executescript(sqlscript)

    def GetLastRowId(self):
        return self.cursor.lastrowid

    def StoreFile(self,scanjobid,path):
        self.ExecuteSQLCommand("INSERT INTO FILES (filepath,scanjobid) VALUES(?,?)",(path,scanjobid))

    def AddScanPath(self,path,pathType,user,password,excNameGlob,excNameRegex,excPathGlob,excPathRegex):
        if pathType is None:
            pathType = GetDefaultPathType()

        if user is None:
            user = ''

        if password is None:
            password = ''

        if excNameGlob is None:
            excNameGlob = []

        if excNameRegex is None:
            excNameRegex = []

        if excPathGlob is None:
            excPathGlob = []

        if excPathRegex is None:
            excPathRegex = []

        excNameGlobDb = '\r'.join(excNameGlob)
        excNameRegexDb = '\r'.join(excNameRegex)

        excPathGlobDb = '\r'.join(excPathGlob)
        excPathRegexDb = '\r'.join(excPathRegex)

        self.ExecuteSQLCommand("INSERT INTO scanpaths (path,pathtype,username,password,globexclusion_name,regexexclusion_name,globexclusion_path,regexexclusion_path) VALUES(?,?,?,?,?,?,?,?)",(path,pathType,user,password,excNameGlobDb,excNameRegexDb,excPathGlobDb,excPathRegexDb))

    def GetScanPaths(self,pathId=None):
        if pathId is None:
            sqlRows = self.GetAllScanPathsRows()
        else:
            sqlRows = self.GetPathWithIdRow(pathId)

        return [ScanPath(sqlRow) for sqlRow in sqlRows]

    def GetAllScanPathsRows(self):
        return self.ExecuteSQLCommand("SELECT * FROM scanpaths")
    
    def GetPathWithIdRow(self,pathId):
        return self.ExecuteSQLCommand("SELECT * FROM scanpaths WHERE id=?",(pathId,))

    def RemoveScanPaths(self,pathId):
        if pathId is None:
            self.ExecuteSQLCommand("DELETE FROM scanpaths")
        else:
            self.ExecuteSQLCommand("DELETE FROM scanpaths WHERE id=?",(pathId,))

    def UpdateScanPath(self,scanPath):
        self.ExecuteSQLCommand('UPDATE scanpaths SET path=?, pathtype=?, username=?, password=?, globexclusion_name=?, regexexclusion_name=?, globexclusion_path=?, regexexclusion_path=? WHERE id=?', (scanPath.path, scanPath.pathtype, scanPath.username, scanPath.password, scanPath.globexclusion_name, scanPath.regexexclusion_name, scanPath.globexclusion_path, scanPath.regexexclusion_path, scanPath.id))

