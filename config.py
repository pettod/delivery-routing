class CONFIG:
    # Constraints
    NUMBER_OF_VEHICLES = 1
    DRIVER_WORKING_HOURS = None  # 8
    DRIVER_MAX_SINGLE_DELIVERY_DISTANCE = None  # 33
    DRIVER_LUNCH_BREAK_DURATION = None  # 1
    DEADLINE_RANGE = None  # (200, 500)

    # Data parameters
    NUMBER_OF_PACKAGES = 30
    DEPOT_COORDINATES = {"x": 0, "y": 0}
    MIN_DISTANCE_FROM_DEPOT = 10
    MAX_DISTANCE_FROM_DEPOT = 50

    # Optimization / debugging
    SEARCH_TIME_LIMIT = 2
    RANDOM_SEED = 23114  # None
