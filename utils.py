import matplotlib.pyplot as plt
import numpy as np
import math


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


def printSolution(manager, routing, solution, packages):
    print(f"Objective: {solution.ObjectiveValue()}")
    vehicle_id = 0
    index = routing.Start(vehicle_id)
    plan_output = "Route for vehicle {}:\n".format(vehicle_id)
    deadlines = "Deadlines of the packages\nDeadline | Route\n"
    route_distance = 0
    while not routing.IsEnd(index):
        plan_output += " {} -> ".format(manager.IndexToNode(index))
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(
            previous_index, index, vehicle_id)
        package_deadline = packages[index-1]["deadline"] if index != len(packages) + 1 else -1
        deadlines += "{:8} | {:4}\n".format(package_deadline, route_distance)
    plan_output += "{}\n".format(manager.IndexToNode(index))
    plan_output += "Distance of the route: {}m\n".format(route_distance)
    print(plan_output)
    print(deadlines)
