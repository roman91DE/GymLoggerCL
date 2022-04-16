#!/usr/bin/python3

from ioManager import IOManager
from dbManager import DatabaseManager
from utilManager import UtilityManager



class Main:
    def __init__(self, userprofile: str, DEBUGMODE=False) -> None:

        self.utilityManager = UtilityManager()
        self.ioManager = IOManager()
        self.databaseManager = DatabaseManager(userprofile)

        if DEBUGMODE:

            self.ioManager.print_workouts(self.utilityManager.parseWorkouts())
            print("EXISTS?", self.databaseManager.databaseExists())


    def run(self):
        pass






if __name__ == "__main__":
    Main(userprofile="roman", DEBUGMODE=True).run()
