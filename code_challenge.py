from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import math
import matplotlib.pyplot as plt
import random
import numpy as np


def printSolution(manager, routing, solution):
    print(f'Objective: {solution.ObjectiveValue()}')
    vehicle_id = 0
    total_distance = 0
    index = routing.Start(vehicle_id)
    plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
    route_distance = 0
    while not routing.IsEnd(index):
        plan_output += ' {} -> '.format(manager.IndexToNode(index))
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(
            previous_index, index, vehicle_id)
    plan_output += '{}\n'.format(manager.IndexToNode(index))
    plan_output += 'Distance of the route: {}m\n'.format(route_distance)
    print(plan_output)
    total_distance += route_distance
    print('Total Distance of all routes: {}m'.format(total_distance))



def solveDeliveryRouting(packages, distance_matrix, driver_working_hours):
    # Read data
    locations = ["Depot"] + [p["location"] for p in packages]
    delivery_deadlines = [p["deadline"] for p in packages]
    max_delivery_distance = [p["max_delivery_distance"] for p in packages]

    # Create the routing index manager
    manager = pywrapcp.RoutingIndexManager(
        len(locations),
        1,
        0,  # Depot 0
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
        dimension_name = "Distance"
        routing.AddDimension(
            transit_callback_index,
            0,  # no slack
            max_delivery_distance[i],  # package max delivery distance
            False,
            dimension_name,
        )
        distance_dimension = routing.GetDimensionOrDie(dimension_name)
        distance_dimension.SetGlobalSpanCostCoefficient(100)
  
        # Set the deadline constraint for each package
        deadline = int(delivery_deadlines[i] * 60)  # Convert deadlines to minutes
        routing.AddDimension(
            transit_callback_index,
            deadline,
            deadline,
            True,
            "Deadline",
        )
  
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
        printSolution(manager, routing, solution)
        return route
  
    return None


def calculateDistanceMatrix(depot_coordinates, data):
    distance_matrix = []
    data = [depot_coordinates] + data

    # Euclidian distance
    for i in range(len(data)):
        location_distances = []
        for j in range(len(data)):
            location_distances.append(math.sqrt(
                (data[i]["x"] - data[j]["x"])**2 +
                (data[i]["y"] - data[j]["y"])**2
            ))
        distance_matrix.append(np.array(location_distances))
    return np.array(distance_matrix)


def plotSolution(depot_coordinates, packages, route):
    plt.plot(depot_coordinates["x"], depot_coordinates["y"], "ro")
    for p in packages:
        plt.plot(p["x"], p["y"], "bo")

    route_x = []
    route_y = []    
    for i in range(len(route)):
        if route[i] == "Depot":
            route_x.append(depot_coordinates["x"])
            route_y.append(depot_coordinates["y"])
        else:
            route_x.append(packages[route[i]-1]["x"])
            route_y.append(packages[route[i]-1]["y"])
    plt.plot(route_x, route_y, color="tab:orange")
    plt.show()


def main():
    number_of_packages = 100

    # Data
    driver_working_hours = 8
    depot_coordinates = {"x": 0, "y": 0}
    packages = []
    for i in range(number_of_packages):

        # Define coordinates that are far enough from the depot
        while True:
            x = random.randint(-50, 50)
            y = random.randint(-50, 50)
            if math.sqrt((x - depot_coordinates["x"])**2 + (y - depot_coordinates["y"])**2) >= 10:
                break

        packages.append({
            "location": i+1,
            "deadline": random.randint(10, 50),
            "max_delivery_distance": random.randint(1000, 10000),
            "x": x,
            "y": y,
        })
    distance_matrix = calculateDistanceMatrix(depot_coordinates, packages)

    route = solveDeliveryRouting(
        packages, distance_matrix, driver_working_hours)

    if route:
        print("Optimal route:", route)
        plotSolution(depot_coordinates, packages, route)
    else:
        print("No feasible solution found.")


main()
