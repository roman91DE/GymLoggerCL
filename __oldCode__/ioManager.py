from pprint import pprint
from typing import List, Dict


class IOManager:

    """
    Input:
    ------
    """

    """
    Output:
    ------
    """

    @staticmethod
    def print_workouts(workouts: List[Dict]) -> None:
        """Pretty prints the enumerated list of workouts"""
        for idx, workout in enumerate(workouts):
            print(f"{idx+1}. Workout:")
            pprint(workout)
