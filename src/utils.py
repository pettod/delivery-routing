import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import random
import math
import os
from PIL import Image


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


def savePlotImages(depot_coordinates, packages, routes):
    plt.plot(depot_coordinates["x"], depot_coordinates["y"], "r^", markersize=15)
    for p in packages:
        plt.plot(p["x"], p["y"], "ko")

    output_path = "output_frames"
    number_of_first_frame_copies = 25
    number_of_last_frame_copies = 100
    number_of_transition_frames = 20
    max_number_of_trips = max([len(route) for route in routes])
    route_x = [[] for i in range(len(routes))]
    route_y = [[] for i in range(len(routes))]
    for i in range(max_number_of_trips):
        for j, route in enumerate(routes):
            if i >= len(route):
                print(i)
                continue
            elif route[i] == "Depot":
                route_x[j].append(depot_coordinates["x"])
                route_y[j].append(depot_coordinates["y"])
            else:
                route_x[j].append(packages[route[i]-1]["x"])
                route_y[j].append(packages[route[i]-1]["y"])
            plt.axis("off")
            plt.plot(route_x[j], route_y[j], color=list(mcolors.TABLEAU_COLORS)[j], linewidth=3)
        plt.savefig(f"{output_path}/{i}.png", dpi=200, bbox_inches="tight")

        # Copy the first frame
        if i == 0:
            for k in range(number_of_first_frame_copies):
                plt.savefig(f"{output_path}/{i}_{k}.png", dpi=200, bbox_inches="tight")

    # Copy the last frame
    for k in range(number_of_last_frame_copies):
        plt.savefig(f"{output_path}/{i+1}_{k}.png", dpi=200, bbox_inches="tight")

    # Create smooth transition
    first_image = Image.open(f"{output_path}/0.png")
    last_image = Image.open(f"{output_path}/{max_number_of_trips-1}.png")
    for l in range(1, 1+number_of_transition_frames):
        blended = Image.blend(last_image, first_image, alpha=l/number_of_transition_frames)
        blended.save(f"{output_path}/{i+2}_{k}_{l}.png")


def plotSolution(depot_coordinates, packages, routes):
    plt.plot(depot_coordinates["x"], depot_coordinates["y"], "r^", markersize=15)
    for p in packages:
        plt.plot(p["x"], p["y"], "ko")

    for route in routes:
        route_x = []
        route_y = []
        for i in range(len(route)):
            if route[i] == "Depot":
                route_x.append(depot_coordinates["x"])
                route_y.append(depot_coordinates["y"])
            else:
                route_x.append(packages[route[i]-1]["x"])
                route_y.append(packages[route[i]-1]["y"])
        plt.plot(route_x, route_y)
    plt.show()


def seedEverything(seed):
    random.seed(seed)
    os.environ["PYTHONASHSEED"] = str(seed)
    np.random.seed(seed)


def printSolution(manager, routing, solution, data):
    def addDeadline(
            index, package_deadline, route_distance, single_delivery_distance):
        return "{:5} | {:8} | {:5} | {:5}\n".format(
            index, package_deadline, route_distance, single_delivery_distance,
        )
    print(f"Objective: {solution.ObjectiveValue()}")
    for vehicle_id in range(data["number_of_vehicles"]):
        index = routing.Start(vehicle_id)
        plan_output = "Route for vehicle {}:\n".format(vehicle_id)
        deadlines = "Deadlines of the packages\nIndex | Deadline | Route | Single delivery distance\n"
        deadlines += addDeadline(
            0,
            -1,
            0,
            0,
        )

        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += " {} -> ".format(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            single_delivery_distance = routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
            route_distance += single_delivery_distance
            i = manager.IndexToNode(index)
            package_deadline = data["packages"][i-1]["deadline"] if i != 0 else -1
            deadlines += addDeadline(
                i,
                package_deadline,
                route_distance,
                single_delivery_distance,
            )
        plan_output += "{}\n".format(manager.IndexToNode(index))
        plan_output += "Distance of the route: {}\n".format(route_distance)
        print(plan_output)
        print(deadlines)
