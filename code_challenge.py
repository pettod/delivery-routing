from ortools.constraint_solver import routing_enums_pb2, pywrapcp

from data import getData
from utils import calculateDistanceMatrix, plotSolution, printSolution


class Routing:
    def __init__(
            self,
            packages,
            depot_coordinates,
            driver_working_hours, 
            driver_max_single_delivery_distance,
            driver_lunch_break_duration,
        ):
        self.packages = packages
        self.driver_working_hours = driver_working_hours
        self.driver_max_single_delivery_distance = driver_max_single_delivery_distance
        self.driver_lunch_break_duration = driver_lunch_break_duration
        self.distance_matrix = calculateDistanceMatrix(depot_coordinates, packages)
        self.locations = ["Depot"] + [p["location"] for p in self.packages]

        # Create the routing index manager
        self.manager = pywrapcp.RoutingIndexManager(
            1 + len(packages),
            1,  # 1 vehicle
            0,  # Depot is the starting point
        )
        self.routing = pywrapcp.RoutingModel(self.manager)

    def addDimension(
            self,
            callback_index,
            slack_max,
            capacity,
            fix_start_cumul_to_zero,
            dimension_name,
            span_cost_coefficient):
        self.routing.AddDimension(
            callback_index,
            slack_max,
            capacity,
            fix_start_cumul_to_zero,
            dimension_name)
        dimension = self.routing.GetDimensionOrDie(dimension_name)
        dimension.SetGlobalSpanCostCoefficient(span_cost_coefficient)

    def addConstraints(self):
        # Define the distance callback
        def distanceCallback(from_index, to_index):
            from_node = self.manager.IndexToNode(from_index)
            to_node = self.manager.IndexToNode(to_index)
            return self.distance_matrix[from_node][to_node]
        transit_callback_index = self.routing.RegisterTransitCallback(distanceCallback)
        self.routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        constraints = []

        # Max distance constraint for each package
        if 1 in constraints:
            for i in range(len(self.packages)):
                self.addDimension(
                    transit_callback_index,
                    0,
                    self.packages[i]["deadline"],  # Package max delivery distance or deadline
                    True,  # Cumulate the distance of the route this far
                    "Deadline",
                    100,
                )
    
        # Set the lunch break constraint
        if 2 in constraints:
            self.addDimension(
                transit_callback_index,
                self.driver_lunch_break_duration,  # Have to stay this long in a node
                self.driver_lunch_break_duration + self.driver_max_single_delivery_distance,  # Don't shorten max single driving distance
                True,  # Cumulate lunch break to the route distance
                "Lunch break",
                100,
            )

        # Driver max single delivery distance
        if 3 in constraints:
            self.addDimension(
                transit_callback_index,
                0,
                self.driver_max_single_delivery_distance,
                False,  # Don't cumulate previous distances
                "Driver max single delivery distance",
                100,
            )

        # Driver max working hours
        if 4 in constraints:
            self.addDimension(
                transit_callback_index,
                0,  # no slack / waiting in a node
                self.driver_working_hours * 60,  # vehicle max travel distance (1 distance unit per minute)
                True,  # Cumulate the distance
                "Working hours",
                100,
            )

    def solve(self):
        self.addConstraints()

        # Set up search parameters and solve
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.time_limit.seconds = 20
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
        driver_lunch_break_duration,
    ) = getData()
    routing = Routing(
        packages,
        depot_coordinates,
        driver_working_hours,
        driver_max_single_delivery_distance,
        driver_lunch_break_duration,
    )
    route = routing.solve()
    if route:
        print("Optimal route:", route)
        plotSolution(depot_coordinates, packages, route)
    else:
        print("No feasible solution found.")


main()
