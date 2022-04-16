#!/usr/bin/python3

import sqlite3
from os import listdir, makedirs
from sys import stderr
from enum import Enum
from typing import Dict, Tuple
from json import load as jsonload
from time import sleep


class Application:
    """
    Application is responsible for the main loop, IO and the delegation of tasks to its DataManager
    """

    class KnownError(RuntimeError):
        """An Error that has been taken into account by the developer"""

        pass

    class MainMenuSelection(Enum):
        """Represents Users Selection for the Main Menu"""

        INIT = 0
        LIST_EXCERCISES = 1
        ADD_EXCERCISE = 2
        SELECT_EXCERCISE = 3
        ADD_RECORD = 4
        LIST_RECORDS = 5
        EXPORT_RECORDS = 6
        QUIT = 10

    def __init__(self) -> None:

        Application.__manageDirectories()

        self.userSelection: Application.MainMenuSelection = (
            Application.MainMenuSelection.INIT
        )
        
        self.dataManager: DataManager = DataManager()
        self.run()

    
    
    def run(self):
        while self.userSelection != Application.MainMenuSelection.QUIT:
            sleep(1)
            self.main_menu()

    def main_menu(self):
        pass

    def list_excercises(self):
        pass

    def add_excercise(self):
        pass

    def select_excercise(self):
        pass

    def add_record(self):
        pass

    def list_records(self):
        pass

    def export_records(self):
        pass

    def backup_to_remote(self):
        pass
    
    @staticmethod
    def __manageDirectories() -> None:
        """Check if required directories are present and create if not"""
        REQUIRED_DIRS = (
            "data",
        )
        PWD_DIRS = listdir()

        for DIR in PWD_DIRS:
            if not DIR in REQUIRED_DIRS:
                makedirs(DIR)

 

class DataManager:
    """Manages all backend related data actions for the main Application"""

    def __init__(self) -> None:
        """
        On first Call it create data/db.sqlite3 and adds all excercises defined in data/excercises.json to the main table
        Establishes both a Connection and a Cursor to the SQLite Database
        """
        self.relativeDatabasePath: str = "data/db.sqlite3"
        self.relativeExcercisePath: str = "data/excercises.json"

        if not self.__databaseExists():
            self.__initNewDB()  # .. also establishes a connection to the new database

        else:  # just connect to existing database
            self.connection = sqlite3.connect(self.relativeDatabasePath)
            self.cursor = self.connection.cursor()

        self.__addExcercisesFromJSON()

    def __databaseExists(self) -> bool:
        """Check if an valid sqlite database exists at relativeDatabasePath"""

        if not self.relativeDatabasePath in listdir("data"):
            return False

        try:  # validate that database is a read- and writeable
            sqlite3.connect(f"file:{self.relativeDatabasePath}?mode=rw", uri=True)
            return True

        except sqlite3.OperationalError:
            print(
                f"Error: Database File <{self.relativeDatabasePath}> exists but connection failed!",
                file=stderr,
            )
            raise Application.KnownError

    def __initNewDB(self):
        """initializes a new sqlite database to track records"""
        self.connection = sqlite3.connect(self.relativeDatabasePath)
        self.cursor = self.connection.cursor()

        SQL_COMMAND = """
            CREATE TABLE IF NOT EXISTS excercises(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                UNIQUE(name, description)
            )
        """

        self.cursor.execute(SQL_COMMAND)
        self.connection.commit()

    def __addExcercisesFromJSON(self) -> None:
        """
        parses all excercises described in data/excercises.json and adds them to the database table <excercises> if they dont already exist
        """

        excercises: Dict = jsonload(open(self.relativeExcercisePath))

        SQL_COMMAND = (
            "INSERT OR IGNORE INTO excercises (name, description) VALUES (?, ?)"
        )

        for name, description in excercises.items():
            self.cursor.execute(SQL_COMMAND, (name, description))

        self.connection.commit()


if __name__ == "__main__":

    try:
        Application()

    except Application.KnownError:
        print(f"Error - Main Application was shutdown for Safety!", file=stderr)

    except:
        print(f"Error - Something unexpected went wrong!", file=stderr)
