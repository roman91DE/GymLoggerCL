#!/usr/bin/python3

from math import nan
import sqlite3
from os import listdir, makedirs
from os.path import exists
from sys import stderr
from shutil import copyfile
from enum import Enum
from typing import Dict, Tuple, List
from json import load as jsonload
from time import sleep
from datetime import datetime
from traceback import print_exc


class Application:
    """
    Application is responsible for the main loop, IO and the delegation of tasks to its DataManager
    """

    class ConsideredError(RuntimeError):
        """An Error that has been taken into account by the developer"""

        pass

    class MainMenuSelection(Enum):
        """Represents Users Selection for the Main Menu"""

        INIT = 0
        LIST_EXCERCISES = 1
        ADD_EXCERCISE = 2
        ADD_RECORD = 3
        LIST_RECORDS = 4
        BACKUP_DB_LOCAL = 5
        BACKUP_DB_REMOTE = 6
        QUIT = 10

    """ SELECTION_MAP is used to map each MainMenuSelection to the according class method of the Application """
    SELECTION_MAP: Dict = {
        MainMenuSelection.INIT: lambda app: app.do_nothing(),
        MainMenuSelection.LIST_EXCERCISES: lambda app: app.list_excercises(),
        MainMenuSelection.ADD_EXCERCISE: lambda app: app.add_excercise(),
        MainMenuSelection.ADD_RECORD: lambda app: app.add_record(),
        MainMenuSelection.LIST_RECORDS: lambda app: app.list_records(),
        MainMenuSelection.BACKUP_DB_LOCAL: lambda app: app.backup_db_local(),
        MainMenuSelection.BACKUP_DB_REMOTE: lambda app: app.backup_db_remote(),
        MainMenuSelection.QUIT: lambda app: app.do_nothing(),
    }

    def __init__(self) -> None:
        """prepare and run the main application"""
        Application.__manageDirectories()

        self.userSelection: Application.MainMenuSelection = (
            Application.MainMenuSelection.INIT
        )

        self.dataManager: DataManager = DataManager()
        self.__run()

    def __run(self) -> None:
        """ run application's main loop """
        Application.__print_logo()
        while self.userSelection != Application.MainMenuSelection.QUIT:
            sleep(0.25)
            self.userSelection = self.run_main_menu()
            Application.SELECTION_MAP[self.userSelection](self)
        else:
            self.dataManager.shutdownDB()

    def run_main_menu(self) -> MainMenuSelection:
        """Display the main menu, prompts User and returns his Selection"""

        def printOptions() -> None:
            """Prints all options for the main menu"""
            print(
                f"""

Main Menu Selections:
----------------------------
\t{Application.MainMenuSelection.LIST_EXCERCISES.value:<3} - List all available Excercises
\t{Application.MainMenuSelection.ADD_EXCERCISE.value:<3} - Add new Excercise
\t{Application.MainMenuSelection.ADD_RECORD.value:<3} - Add new Record
\t{Application.MainMenuSelection.LIST_RECORDS.value:<3} - List Record
\t{Application.MainMenuSelection.BACKUP_DB_LOCAL.value:<3} - Backup Database to local Folder
\t{Application.MainMenuSelection. BACKUP_DB_REMOTE.value:<3} - Backup Database to remote Server
\t{Application.MainMenuSelection.QUIT.value:<3} - Quit
            """
            )

        def promptUser() -> Application.MainMenuSelection:
            """prompt the user to select an option from the main menu"""
            try:
                BUF = int(input("Enter Number: "))
                return Application.MainMenuSelection(BUF)
            except ValueError:
                print("Invalid Input, please try again!")
                return promptUser()

        printOptions()
        return promptUser()

    def list_excercises(self) -> None:
        """prints all excercises that have been added to the database"""

        print(
            f"""
Available Excercises:
-------------------------
"""
        )
        for (id, name, description) in self.dataManager.getAllExcercises():
            print(f"#{id:<3}\t{name}\n\t-{description}\n")

    def add_excercise(self) -> None:
        """read a new excercise from user input and add it to the database"""
        try:
            NAME = input("Enter a name for the new excercise:")
            DESCRIPTION = input(f"Enter a short Description for {NAME}: ")
        except ValueError:
            print(f"Error: Invalid input, please try again!", file=stderr)
            self.add_excercise()

        self.dataManager.addNewExcercise(NAME, DESCRIPTION)

    def add_record(self) -> None:
        """add new record(s) for the selected excercise to the database"""
        EXCERCISE_ID: int = self.__select_excercise()
        RECORDS: List[Tuple[float, int]] = []

        counter: int = 1
        buffer: str = ""

        while True:
            print(f"\nSet #{counter}, type q[uit] to finish the excercise:")
            buffer = input("Enter WEIGHT REPS:  ")

            if buffer[0].lower() == "q":
                break

            try:
                WEIGHT, REPS = map(float, buffer.split())
            except ValueError:
                print(f"Error: Invalid Input, please try again!")
                continue

            RECORDS.append((WEIGHT, int(REPS)))
            counter += 1

        if len(RECORDS) < 1:
            print("Warning: Aborted Operation for empty Record")
            return

        self.dataManager.addNewRecords(EXCERCISE_ID, RECORDS)

    def __select_excercise(self) -> int:
        """prompt user to select an excercise by its id"""
        self.list_excercises()
        try:
            return int(input("Select Excercise by its number: "))
        except ValueError:
            print(
                f"Error: Invalid Input, please select excercise by its integer index:"
            )
            return self.__select_excercise()

    def list_records(self) -> None:
        """print all records for a user selected excercise"""
        EXCERCISE_ID: int = self.__select_excercise()

        records: List[Tuple[str, int, float]] = self.dataManager.getRecordsForExcercise(
            EXCERCISE_ID
        )

        print(
            "\nTime\t\tRepetitions\tWeight\n------------------------------------------------"
        )

        for (timestamp, reps, weight) in records:
            print(f"""{timestamp[:-7]:>10}\t{reps:>3}\t{weight:>4.2f}""")

    def do_nothing(self) -> None:
        """does nothing..."""
        pass

    def backup_db_local(self) -> None:
        print("Backup of Database will be written to the Directory ./backups/")
        self.dataManager.backupLocal()

    def backup_db_remote(self) -> None:
        print("Feature has not been implemented yet...")

    @staticmethod
    def __manageDirectories() -> None:
        """Check if required directories are present and create them if they aren't"""
        REQUIRED_DIRS: List[str] = ["data", "backups", "logo"]
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

    def getAllExcercises(self) -> List[Tuple[int, str, str]]:
        """Query Database for all available Excercses and return results"""

        SQL_COMMAND = """
        SELECT id, name, description 
        FROM excercises
        """
        try:
            self.cursor.execute(SQL_COMMAND)
            return self.cursor.fetchall()

        except sqlite3.OperationalError as Err:
            print(
                f"Database Operation Error: Failed to fetch results for Querry: {Err}/n",
                file=stderr,
            )
            raise Application.ConsideredError

    def getRecordsForExcercise(
        self, excercise_id: int
    ) -> List[Tuple[str, int, float]]:  # return type?

        SQL_COMMAND = """
        SELECT timestamp, reps, weight 
        FROM records 
        WHERE (excercise_id=?) 
        ORDER BY timestamp DESC
        """
        self.cursor.execute(SQL_COMMAND, (excercise_id,))
        return self.cursor.fetchall()

    def addNewExcercise(self, name: str, description: str) -> None:
        """Insert new record for <name> to the table <excercise>"""

        SQL_COMMAND = """
        INSERT INTO excercises (name, description) 
        VALUES (?, ?)
        """

        try:
            self.cursor.execute(SQL_COMMAND, (name, description))
            self.connection.commit()

        except sqlite3.OperationalError as Err:
            print(
                f"Database Operation Error: Failed to insert new Excercise: {Err}/n",
                file=stderr,
            )
            raise Application.ConsideredError

    def addNewRecords(self, excerciseID: int, records: List[Tuple[float, int]]) -> None:
        """Adds new record(s) to the table <records>"""

        SQL_COMMAND = """
        INSERT INTO records (excercise_id, timestamp, weight, reps) 
        VALUES (?, ?, ?, ?)
        """
        for (
            weight,
            reps,
        ) in records:  # single record: Tuple["weight":float, "reps": int]
            self.cursor.execute(
                SQL_COMMAND, (excerciseID, datetime.now(), str(weight), str(reps))
            )

        self.connection.commit()

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
            raise Application.ConsideredError

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

        SQL_COMMAND = """
        CREATE TABLE IF NOT EXISTS records(
                excercise_id NOT NULL,
                timestamp TEXT NOT NULL,
                weight FLOAT NOT NULL,
                reps INT NOT NULL,
                PRIMARY KEY (excercise_id, timestamp)
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

        SQL_COMMAND = """
            INSERT OR IGNORE INTO excercises (name, description)
            VALUES (?, ?)
        """

        for name, description in excercises.items():
            self.cursor.execute(SQL_COMMAND, (name, description))

        self.connection.commit()

    def backupLocal(self) -> None:
        copyfile(self.relativeDatabasePath, f"backups/backup.sqlite3")

    def shutdownDB(self) -> None:
        self.cursor.close()
        self.connection.close()


if __name__ == "__main__":

    try:
        Application()

    except Application.ConsideredError as Err:
        print(
            f"Error - Main Application was shutdown!\nError: {Err.with_traceback}",
            file=stderr,
        )
        print_exc(file=stderr)

    except Exception as UnknownError:
        print(
            f"Error - Something unexpected went wrong! Error: {UnknownError}\n{UnknownError.with_traceback}",
            file=stderr,
        )
        print_exc(file=stderr)
