#!/usr/bin/python3

from printer import PrintingManager
from database import DatabaseManager
from utility import UtilityManager



class Main:
    def __init__(self, userprofile: str, DEBUGMODE=False) -> None:

        self.utilityManager = UtilityManager()
        self.printingManager = PrintingManager()
        self.databaseManager = DatabaseManager(userprofile)

        if DEBUGMODE:

            self.printingManager.workouts(self.utilityManager.parseWorkouts())
            print("EXISTS?", self.databaseManager.databaseExists())


    def run(self):
        pass






if __name__ == "__main__":
    Main(userprofile="roman", DEBUGMODE=True).run()
