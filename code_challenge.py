from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import math
import random
import numpy as np

from utils import calculateDistanceMatrix, plotSolution, printSolution


def solveDeliveryRouting(packages, distance_matrix, driver_working_hours):
    # Read data
    locations = ["Depot"] + [p["location"] for p in packages]
    delivery_deadlines = [p["deadline"] for p in packages]
    max_delivery_distance = [p["max_delivery_distance"] for p in packages]

    # Create the routing index manager
    manager = pywrapcp.RoutingIndexManager(
        len(locations),
        1,
        0,  # Depot is the starting point
    )
    
    # Create the routing model
    routing = pywrapcp.RoutingModel(manager)
  
    # Define the distance callback
    def distanceCallback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]
    transit_callback_index = routing.RegisterTransitCallback(distanceCallback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
  
    # Define the maximum distance constraint for each package
    for i in range(len(packages)):
        dimension_name = "Deadline"
        routing.AddDimension(
            transit_callback_index,
            0,  # No slack
            delivery_deadlines[i],  # Package max delivery distance / deadline
            True,
            dimension_name,
        )
        deadline_dimension = routing.GetDimensionOrDie(dimension_name)
        deadline_dimension.SetGlobalSpanCostCoefficient(100)
  
    # Set the lunch break constraint
    #lunch_break_duration = 60  # minutes
    #routing.AddDimension(
    #    transit_callback_index,
    #    lunch_break_duration,
    #    driver_working_hours * 60,  # working hours in minutes
    #    True,
    #    "Working Hours",
    #)

    # Set up search parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem
    solution = routing.SolveWithParameters(search_parameters)
  
    if solution:
        # Get the optimal route
        route = []
        index = routing.Start(0)
        while not routing.IsEnd(index):
            route.append(locations[index])
            index = solution.Value(routing.NextVar(index))
        route.append(locations[0])
        printSolution(manager, routing, solution, packages)
        return route
  
    return None


def defineData(
        number_of_packages=30,
        driver_working_hours=8,
        min_distance_from_depot=10,
        max_distance_from_depot=50,
        depot_coordinates={"x": 0, "y": 0},
    ):
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

        packages.append({
            "location": i+1,
            "deadline": random.randint(600, 700),
            "max_delivery_distance": random.randint(1000, 10000),
            "x": x,
            "y": y,
        })
    return (
        packages,
        depot_coordinates,
        driver_working_hours,
    )


def main():
    (
        packages,
        depot_coordinates,
        driver_working_hours,
    ) = defineData()
    distance_matrix = calculateDistanceMatrix(depot_coordinates, packages)
    route = solveDeliveryRouting(
        packages, distance_matrix, driver_working_hours)
    if route:
        print("Optimal route:", route)
        plotSolution(depot_coordinates, packages, route)
    else:
        print("No feasible solution found.")


main()
