from printer import PrintingFacility
from database import DatabaseFacility
import utilities



class GymLogger:
    def __init__(self) -> None:
        self.workouts = utilities.parseWorkouts()
        self.printingFacility = PrintingFacility()
        self.databaseFacility = DatabaseFacility()

        self.printingFacility.workouts(self.workouts)
        print("EXISTS?", self.databaseFacility.databaseExists())


    def run(self):
        pass