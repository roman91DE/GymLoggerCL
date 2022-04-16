from pprint import pprint
from typing import List, Dict


class PrintingManager:

    def workouts(self, workouts: List[Dict]) -> None:
        """Pretty prints the enumerated list of workouts"""
        for idx, workout in enumerate(workouts):
            print(f"{idx+1}. Workout:")
            pprint(workout)
        