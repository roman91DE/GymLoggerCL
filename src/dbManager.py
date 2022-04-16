import sqlite3
from os import listdir
from sys import stderr
from typing import List


class DatabaseManager:
    def __init__(self, user_profile: str) -> None:
        """Basic setup  and initialization of Object"""

        self.user_profile: str = user_profile
        self.db_path: str = "__INVALID__"

        if not self.databaseExists():
            self.initNewDB()
        else:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()

    def databaseExists(self) -> bool:
        """Checks if an valid sqlite database has already been instantiated at ../db"""
        files: List[str] = listdir("db")

        if len(files) == 0:
            return False

        elif len(files) > 0:
            for file in files:
                if file.startswith(f"{self.user_profile}.sqlite3"):
                    self.db_path = f"db/{file}"
        else:
            return False

        try:
            sqlite3.connect(
                f"file:{self.db_path}?mode=rw", uri=True
            )  # Checks if file is really a useable sqlite db
            return True

        except sqlite3.OperationalError:
            print(
                f"Warning: Database File <{self.db_path}> exists but connection failed!",
                file=stderr,
            )
            return False

    def initNewDB(self):
        """initializes a new sqlite database to track workouts"""
        self.connection = sqlite3.connect(f"db/{self.user_profile}.sqlite3")
        self.cursor = self.connection.cursor()

        SQL_CREATE_CMD = """CREATE TABLE gym_log(
            timestamp INTEGER,
            excercise TEXT,
            rep_scheme TEXT,
            weight_scheme TEXT,
            total_weight REAL
        )"""

        self.cursor.execute(SQL_CREATE_CMD)
        self.connection.commit()
