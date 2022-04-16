from os import listdir
from typing import Dict, List
from json import load as jload


class UtilityManager:

    @staticmethod
    def parseWorkouts() -> List[Dict]:
        """Parses all .json files in ../workouts and returns them as a set of python dictionaries"""

        def parseFile(path: str) -> Dict:
            return jload(open(path))

        files = listdir("workouts")
        workouts = []
        
        for file in files:
            workouts.append(parseFile(f"workouts/{file}"))

        return workouts
