import math
import random
from config import CONFIG
from src.utils import seedEverything


def getData():
    if CONFIG.RANDOM_SEED:
        seedEverything(CONFIG.RANDOM_SEED)  # Use the same randomness

    # Read config data
    number_of_packages = CONFIG.NUMBER_OF_PACKAGES
    driver_working_hours = CONFIG.DRIVER_WORKING_HOURS
    driver_max_single_delivery_distance = CONFIG.DRIVER_MAX_SINGLE_DELIVERY_DISTANCE
    driver_lunch_break_duration = CONFIG.DRIVER_LUNCH_BREAK_DURATION
    number_of_vehicles = CONFIG.NUMBER_OF_VEHICLES
    min_distance_from_depot = CONFIG.MIN_DISTANCE_FROM_DEPOT
    max_distance_from_depot = CONFIG.MAX_DISTANCE_FROM_DEPOT
    depot_coordinates = CONFIG.DEPOT_COORDINATES
    deadline_range = CONFIG.DEADLINE_RANGE

    # Define the locations of the packages
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

        if deadline_range:
            deadline = random.randint(deadline_range[0], deadline_range[0])
        else:
            deadline = 0

        packages.append({
            "location": i+1,
            "deadline": deadline,
            "x": x,
            "y": y,
        })
    return {
        "packages": packages,
        "depot_coordinates": depot_coordinates,
        "driver_working_hours": driver_working_hours,
        "driver_max_single_delivery_distance": driver_max_single_delivery_distance,
        "driver_lunch_break_duration": driver_lunch_break_duration,
        "number_of_vehicles": number_of_vehicles,
    }
