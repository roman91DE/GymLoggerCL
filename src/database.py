import sqlite3
from os import listdir
from sys import stderr
from typing import List


class DatabaseFacility:

    def __init__(self) -> None:
        
        if not DatabaseFacility.databaseExists():
            DatabaseFacility.initNewDB()

        

    def databaseExists() -> bool:
        """Checks if an valid sqlite database has already been instantiated at ../database"""
        files: List[str] = listdir("../database")

        if len(files) == 0:
            return False

        if len(files) > 1:
            print(f"Error: Multiple Files <{files}> exist at database directory! Clean it up manually!", file=stderr)
            raise RuntimeError

        elif not files[0].lower().endswith((".sqlite3", ".sqlite", ".db")):
            return False

        try:
            sqlite3.connect(f'file:{files[0]}?mode=rw', uri=True)   # Checks if file is really a useable sqlite db
            
        except sqlite3.OperationalError:
            print(f"Warning: Database File <{files}> exists but connection failed!", file=stderr)
            return False
        
        return True


    def initNewDB():
        pass