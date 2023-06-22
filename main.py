from ortools.constraint_solver import routing_enums_pb2, pywrapcp

from config import CONFIG
from src.data import getData
from src.utils import calculateDistanceMatrix, plotSolution, printSolution


class Routing:
    def __init__(self, data):
        self.data = data
        self.distance_matrix = calculateDistanceMatrix(
            self.data["depot_coordinates"], self.data["packages"])
        self.locations = ["Depot"] + [p["location"] for p in self.data["packages"]]

        # Create the routing index manager
        self.manager = pywrapcp.RoutingIndexManager(
            len(self.distance_matrix),
            self.data["number_of_vehicles"],
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

        # Max distance constraint for each package
        if CONFIG.DEADLINE_RANGE:
            for i in range(len(self.data["packages"])):
                self.addDimension(
                    transit_callback_index,
                    0,
                    self.data["packages"][i]["deadline"],  # Package max delivery distance or deadline
                    True,  # Cumulate the distance of the route this far
                    "Deadline",
                    100,
                )
    
        # Set the lunch break constraint
        if CONFIG.DRIVER_LUNCH_BREAK_DURATION:
            self.addDimension(
                transit_callback_index,
                self.data["driver_lunch_break_duration"],  # Have to stay this long in a node
                self.data["driver_lunch_break_duration"] + self.data["driver_max_single_delivery_distance"],  # Don't shorten max single driving distance
                True,  # Cumulate lunch break to the route distance
                "Lunch break",
                100,
            )

        # Driver max single delivery distance
        if CONFIG.DRIVER_MAX_SINGLE_DELIVERY_DISTANCE:
            self.addDimension(
                transit_callback_index,
                0,
                self.data["driver_max_single_delivery_distance"],
                False,  # Don't cumulate previous distances
                "Driver max single delivery distance",
                100,
            )

        # Driver max working hours
        if CONFIG.DRIVER_WORKING_HOURS:
            self.addDimension(
                transit_callback_index,
                0,  # no slack / waiting in a node
                self.data["driver_working_hours"] * 60,  # vehicle max travel distance (1 distance unit per minute)
                True,  # Cumulate the distance
                "Working hours",
                100,
            )

    def solve(self):
        self.addConstraints()

        # Set up search parameters and solve
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.time_limit.seconds = CONFIG.SEARCH_TIME_LIMIT

        # Try different strategies if some are too slow to find a solution
        solution_strategies = [
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC,
            routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION,
            routing_enums_pb2.FirstSolutionStrategy.BEST_INSERTION,
            routing_enums_pb2.FirstSolutionStrategy.CHRISTOFIDES,
            routing_enums_pb2.FirstSolutionStrategy.ALL_UNPERFORMED,
            routing_enums_pb2.FirstSolutionStrategy.EVALUATOR_STRATEGY,
            routing_enums_pb2.FirstSolutionStrategy.FIRST_UNBOUND_MIN_VALUE,
            routing_enums_pb2.FirstSolutionStrategy.GLOBAL_CHEAPEST_ARC,
            routing_enums_pb2.FirstSolutionStrategy.LOCAL_CHEAPEST_ARC,
            routing_enums_pb2.FirstSolutionStrategy.LOCAL_CHEAPEST_COST_INSERTION,
            routing_enums_pb2.FirstSolutionStrategy.LOCAL_CHEAPEST_INSERTION,
        ]
        for strategy in solution_strategies:
            search_parameters.first_solution_strategy = strategy
            solution = self.routing.SolveWithParameters(search_parameters)
            if solution:
                break
    
        if solution:
            routes = []
            for i in range(self.data["number_of_vehicles"]):
                route = []
                index = self.routing.Start(i)
                while not self.routing.IsEnd(index):
                    route.append(self.locations[self.manager.IndexToNode(index)])
                    index = solution.Value(self.routing.NextVar(index))
                route.append(self.locations[0])
                routes.append(route)
                print(f"Optimal route {i}:", route)
            printSolution(self.manager, self.routing, solution, self.data)
            plotSolution(self.data["depot_coordinates"], self.data["packages"], routes)
        else:
            print("No feasible solution found.")


def main():
    data = getData()
    routing = Routing(data)
    routing.solve()


main()
