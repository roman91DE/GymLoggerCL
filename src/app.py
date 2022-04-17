#!/usr/bin/python3

import sqlite3
from os import listdir, makedirs
from os.path import exists
from sys import stderr
from enum import Enum
from typing import Dict, Tuple, List
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
        ADD_RECORD = 3
        LIST_RECORDS = 4
        EXPORT_RECORDS = 5
        QUIT = 10

    """ SELECTION_MAP is used to map each MainMenuSelection to the according class method of the Application """
    SELECTION_MAP: Dict = {
        MainMenuSelection.INIT: lambda app: None,
        MainMenuSelection.LIST_EXCERCISES: lambda app: app.list_excercises(),
        MainMenuSelection.ADD_EXCERCISE: lambda app: app.add_excercise(),
        MainMenuSelection.ADD_RECORD: lambda app: app.add_record(),
        MainMenuSelection.LIST_RECORDS: lambda app: app.list_records(),
        MainMenuSelection.EXPORT_RECORDS: lambda app: app.export_records(),
        MainMenuSelection.QUIT: lambda app: None,
    }

    def __init__(self) -> None:

        Application.__manageDirectories()

        self.userSelection: Application.MainMenuSelection = (
            Application.MainMenuSelection.INIT
        )

        self.dataManager: DataManager = DataManager()
        self.run()

    def run(self) -> None:
        Application.__print_logo()
        while self.userSelection != Application.MainMenuSelection.QUIT:
            sleep(0.25)
            self.userSelection = self.run_main_menu()
            Application.SELECTION_MAP[self.userSelection](self)

    def run_main_menu(self) -> MainMenuSelection:
        """Display the main menu, prompts User and returns his Selection"""

        def printOptions() -> None:
            print(
                f"""
Main Menu Selections:
\t{Application.MainMenuSelection.LIST_EXCERCISES.value:<3} - List all available Excercises
\t{Application.MainMenuSelection.ADD_EXCERCISE.value:<3} - Add new Excercise
\t{Application.MainMenuSelection.ADD_RECORD.value:<3} - Add new Record
\t{Application.MainMenuSelection.LIST_RECORDS.value:<3} - List Record
\t{Application.MainMenuSelection.EXPORT_RECORDS.value:<3} - Export Records
\t{Application.MainMenuSelection.QUIT.value:<3} - Quit
            """
            )

        def promptUser() -> Application.MainMenuSelection:
            try:
                BUF = int(input("Enter Number: "))
                return Application.MainMenuSelection(BUF)
            except ValueError:
                print("Invalid Input, please try again!")
                return promptUser()

        printOptions()
        return promptUser()

    def list_excercises(self) -> None:
        print("Not implemented yet...")

    def add_excercise(self) -> None:
        print("Not implemented yet...")

    def select_excercise(self) -> None:
        print("Not implemented yet...")

    def add_record(self) -> None:
        print("Not implemented yet...")

    def list_records(self) -> None:
        print("Not implemented yet...")

    def export_records(self) -> None:
        print("Not implemented yet...")

    def backup_to_remote(self) -> None:
        print("Not implemented yet...")

    @staticmethod
    def __manageDirectories() -> None:
        """Check if required directories are present and create if not"""
        REQUIRED_DIRS: List[str] = ["data", "plots", "logo"]
        PWD_DIRS: List[str] = listdir()

        for DIR in REQUIRED_DIRS:
            if not DIR in PWD_DIRS:
                makedirs(f"{DIR}")

    @staticmethod
    def __print_logo() -> None:
        """Prints the content of the text file logo/logo.txt"""
        try:
            with open("logo/logo.txt", mode="r") as fstream:
                for line in fstream:
                    print(line)
        except FileNotFoundError:
            print("GymLogger - CL")
            print(f"Warning: Logo File at logo/logo.txt not found", file=stderr)


class DataManager:
    """Manages all backend related data actions for the main Application"""

    def __init__(self) -> None:
        """
        On first Call it creates data/db.sqlite3 and adds all excercises defined in data/excercises.json to the main table
        Establishes both a Connection and a Cursor to the SQLite Database as member variables
        """
        self.relativeDatabasePath: str = "data/db.sqlite3"
        self.relativeExcercisePath: str = "data/excercises.json"

        if not self.__databaseExists():
            self.__initNewDB()  # ... also establishes a connection to the new database

        else:  # ... just connect to existing database
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

    def __initNewDB(self) -> None:
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

        if not exists(self.relativeExcercisePath):
            print(f"Info: The File <data/excercises.json> does not exist", file=stderr)
            return

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
        print(f"Error - Main Application was shutdown!", file=stderr)

    except Exception as UnknownError:
        print(
            f"Error - Something unexpected went wrong! Error: {UnknownError}",
            file=stderr,
        )
