from ortools.constraint_solver import routing_enums_pb2, pywrapcp

from data import getData
from utils import calculateDistanceMatrix, plotSolution, printSolution


class Routing:
    def __init__(
            self, packages, depot_coordinates, driver_working_hours, 
            driver_max_single_delivery_distance,):
        self.driver_working_hours = driver_working_hours
        self.driver_max_single_delivery_distance = driver_max_single_delivery_distance
        self.packages = packages
        self.distance_matrix = calculateDistanceMatrix(depot_coordinates, packages)
        self.locations = ["Depot"] + [p["location"] for p in self.packages]

        # Create the routing index manager
        self.manager = pywrapcp.RoutingIndexManager(
            1 + len(packages),
            1,  # 1 vehicle
            0,  # Depot is the starting point
        )
        self.routing = pywrapcp.RoutingModel(self.manager)

    def addConstraints(self):
        # Define the distance callback
        def distanceCallback(from_index, to_index):
            from_node = self.manager.IndexToNode(from_index)
            to_node = self.manager.IndexToNode(to_index)
            return self.distance_matrix[from_node][to_node]
        transit_callback_index = self.routing.RegisterTransitCallback(distanceCallback)
        self.routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Define the maximum distance constraint for each package
        dimension_name = "Deadline"
        for i in range(len(self.packages)):
            self.routing.AddDimension(
                transit_callback_index,
                0,  # No slack
                self.packages[i]["deadline"],  # Package max delivery distance / deadline
                True,
                dimension_name,
            )
        #deadline_dimension = routing.GetDimensionOrDie(dimension_name)
        #deadline_dimension.SetGlobalSpanCostCoefficient(100)
    
        # Set the lunch break constraint
        #lunch_break_duration = 60  # minutes
        #routing.AddDimension(
        #    transit_callback_index,
        #    lunch_break_duration,
        #    driver_working_hours * 60,  # working hours in minutes
        #    True,
        #    "Working Hours",
        #)

        # Set driver max single delivery distance
        #routing.AddDimension(
        #    transit_callback_index,
        #    0,
        #    driver_max_single_delivery_distance,
        #    True,
        #    "Driver max single delivery distance",
        #)

    def solve(self):
        self.addConstraints()

        # Set up search parameters and solve
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.time_limit.seconds = 30
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
        solution = self.routing.SolveWithParameters(search_parameters)
    
        if solution:
            route = []
            index = self.routing.Start(0)
            while not self.routing.IsEnd(index):
                route.append(self.locations[index])
                index = solution.Value(self.routing.NextVar(index))
            route.append(self.locations[0])
            printSolution(self.manager, self.routing, solution, self.packages)
            return route
    
        return None


def main():
    (
        packages,
        depot_coordinates,
        driver_working_hours,
        driver_max_single_delivery_distance,
    ) = getData()
    routing = Routing(
        packages, depot_coordinates, driver_working_hours, 
        driver_max_single_delivery_distance,
    )
    route = routing.solve()
    if route:
        print("Optimal route:", route)
        plotSolution(depot_coordinates, packages, route)
    else:
        print("No feasible solution found.")


main()
