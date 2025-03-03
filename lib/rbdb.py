import sqlite3
from lib.rbutility import getDbFileName

class RbDb:
    def __init__(self):
        dbName = getDbFileName()
        self.con = sqlite3.connect(dbName)
        self.cursor = self.con.cursor()

    def __del__(self):
        self.cursor.close()
        self.con.close()

    def addFinishTimes(self, finishInfo):
        pass

    def createTable(self, tableName: str, tableColumns: tuple):
        if self.tableExists(tableName):
            return True
        if len(tableColumns) < 1:
            return False
        columnText = ', '.join(tableColumns)
        self.cursor.execute(f'CREATE TABLE "{tableName}"({columnText})')
        return self.tableExists(tableName)

    def deleteTable(self, tableName: str):
        if not self.tableExists(tableName):
            return False
        self.cursor.execute(f'DROP TABLE "{tableName}"')
        return True

    def saveChanges(self):
        self.con.commit()

    def tableExists(self, tableName: str):
        result = self.cursor.execute(f'SELECT name FROM sqlite_master WHERE name="{tableName}"')
        return result.fetchone() is not None

    def addRows(self, tableName: str, grid: list[tuple]):
        if len(grid) < 1 or len(grid[0]) < 1:
            return False
        placeholders = ', '.join(['?'] * len(grid[0]))
        qry = f'INSERT INTO "{tableName}" VALUES({placeholders})'
        self.cursor.executemany(qry, grid)
        return True

    def addRow(self, tableName: str, row: tuple):
        if len(row) < 1:
            return False
        placeholders = ', '.join(['?'] * len(row))
        qry = f'INSERT INTO "{tableName}" VALUES({placeholders})'
        self.cursor.execute(qry, row)
        return True

    def removeRows(self, tableName: str, columnName: str, columnValue):
        if len(columnName) < 1 or len(columnValue) < 1:
            return False
        qry = f'DELETE FROM "{tableName}" WHERE {columnName} = ?'
        self.cursor.execute(qry, (columnValue,))
        return True

    def getRows(self, tableName: str, columnNames: tuple = (), columnValue = ''):
        columnNamesText = '*'
        if columnNames:
            columnNamesText = ', '.join(columnNames)
        qry = f'SELECT {columnNamesText} FROM "{tableName}"'
        if columnValue:
            qry += f' WHERE {columnValue} = ?'
            self.cursor.execute(qry, (columnValue,))
        else:
            self.cursor.execute(qry)
        return self.cursor.fetchall()