import math
import random
from utils import seedEverything


def getData(
        number_of_packages=30,
        driver_working_hours=8,
        driver_max_single_delivery_distance=33,
        driver_lunch_break_duration=1,
        min_distance_from_depot=10,
        max_distance_from_depot=50,
        depot_coordinates={"x": 0, "y": 0},
    ):
    seedEverything(23114)
    max_package_coordinate = depot_coordinates["x"] + max_distance_from_depot
    min_package_coordinate = depot_coordinates["y"] - max_distance_from_depot
    packages = []
    for i in range(number_of_packages):

        # Define coordinates that are far enough from the depot
        while True:
            x = random.randint(min_package_coordinate, max_package_coordinate)
            y = random.randint(min_package_coordinate, max_package_coordinate)
            if math.sqrt(
                (x - depot_coordinates["x"])**2 +
                (y - depot_coordinates["y"])**2
            ) >= min_distance_from_depot:
                break

        # Force few short deadlines
        deadline = random.randint(5000, 10000) #if i > 1 else 150 #random.randint(150, 200)

        packages.append({
            "location": i+1,
            "deadline": deadline,
            "x": x,
            "y": y,
        })
    return (
        packages,
        depot_coordinates,
        driver_working_hours,
        driver_max_single_delivery_distance,
        driver_lunch_break_duration,
    )
