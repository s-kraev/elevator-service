import logging
import random
import sys
import time
from enum import Enum

logger = logging.getLogger()
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class ElevatorError(Exception):
    """Exception class for Elevator-related errors."""


class Direction(Enum):
    IDLE = 0
    UP = 1
    DOWN = -1


class Passenger:
    population: int = 0

    def __init__(self, floors: int, start_floor: int = None, target_floor: int = None):
        if floors < 2:
            raise ValueError("Floors count must be more than 1")
        self.id: int = Passenger.population
        Passenger.population += 1
        self.start_floor: int = random.randint(0, floors-1) if start_floor is None else start_floor
        self.target_floor: int = random.choice([i for i in range(floors) if i != self.start_floor]) if target_floor is None else target_floor
        self.direction: Direction = (Direction.UP if self.start_floor < self.target_floor else Direction.DOWN)
        self.finished: bool = False
        self.in_elevator: bool = False
        self.elevator_spot: bool = False

    def __repr__(self) -> str:
        return f"Passenger Start: {self.start_floor}, Target: {self.target_floor}"

    def arrived(self, floor: int) -> bool:
        """Returns true if the passenger has arrived at where they wanted to go."""
        return floor == self.target_floor

    def waiting(self) -> bool:
        """Returns True if the passenger is not in the elevator, and they haven't got where they are going."""
        return not self.in_elevator and not self.finished


class Elevator:
    def __init__(self, max_floor: int, capacity: int = 6):
        self.max_floor: int = max_floor
        self.capacity: int = capacity
        self.elevator_population: list[Passenger] = []
        self.floor_population: list[int] = [0] * (max_floor)
        self.floor: int = 0
        self.doors_opened: bool = False
        self.direction: Direction = Direction.IDLE
        self.target_floor: int = 0
        self.log: list[str] = []

    def __repr__(self) -> str:
        return f"Elevator Current: {self.floor} {self.direction.name}, Target: {self.target_floor}"

    @property
    def is_full(self) -> bool:
        return len(self.elevator_population) == self.capacity

    @property
    def idle(self) -> bool:
        return self.direction == Direction.IDLE

    @property
    def going_up(self) -> bool:
        return self.direction == Direction.UP

    @property
    def going_down(self) -> bool:
        return self.direction == Direction.DOWN

    def add_to_log(self, entry: str):
        """
        Add an entry to the elevator's log.
        self.log needed for testing purposes
        """
        self.log.append(entry)
        logger.info(entry)

    def open_doors(self):
        if not self.doors_opened:
            self.doors_opened = True
            self.add_to_log("Opened doors")

    def close_doors(self):
        if self.doors_opened:
            self.doors_opened = False
            self.add_to_log("Closed doors")

    def call_elevator(self, floor: int):
        """Call elevator from the outside."""
        self.floor_population[floor] += 1

    def onboard(self, passenger: Passenger):
        """
        Onboard a passenger into the elevator.
        A passenger can only be onboarded if the elevator is at the same floor, goes in the same direction,
        and there is space available.
        """
        if passenger.start_floor != self.floor:
            return
        if self.is_full:
            self.add_to_log(f"Elevator is full. Passenger {passenger.id} needs to wait.")
            return
        if self.direction == passenger.direction or self.floor == 0 or self.floor == self.max_floor - 1 or self.floor == self.target_floor:
            self.open_doors()
            self.elevator_population.append(passenger)
            passenger.in_elevator = True
            self.floor_population[passenger.start_floor] -= 1
            self.add_to_log(f"Passenger {passenger.start_floor} -> {passenger.target_floor} entered at floor {self.floor}")

    def remove(self, passenger: Passenger):
        """Remove a passenger from the elevator when they reach their target floor."""
        if passenger.target_floor != self.floor:
            return
        self.open_doors()
        passenger.in_elevator = False
        passenger.finished = True
        self.elevator_population.remove(passenger)
        self.add_to_log(f"Passenger {passenger.start_floor} -> {passenger.target_floor} exited at floor {self.floor}")

    def get_elevator_buttons(self) -> list[bool]:
        """Get the status of the elevator buttons indicating passengers target floors."""
        elevator_buttons = [False] * self.max_floor
        for passenger in self.elevator_population:
            elevator_buttons[passenger.target_floor] = True
        return elevator_buttons

    def move(self):
        """Move the elevator to the next floor based on the target floor and direction."""
        elevator_buttons = self.get_elevator_buttons()
        # Get floors where buttons are pressed
        floors_people_want_to_go_to = [i for i in range(len(elevator_buttons)) if elevator_buttons[i]]
        floors_people_want_to_go_to.extend(
            [floor for floor in range(self.max_floor) if bool(self.floor_population[floor])]
        )
        if not floors_people_want_to_go_to:
            raise ElevatorError("Elevator is moving, but no buttons pressed")
        highest_floor = max(floors_people_want_to_go_to)
        lowest_floor = min(floors_people_want_to_go_to)
        # If elevator reached highest or lowest needed floor - change direction. Set direction for idle
        if self.idle:
            self.target_floor = highest_floor
            self.direction = Direction.UP if highest_floor > self.floor else Direction.DOWN
        elif self.going_up and self.floor >= highest_floor:
            self.target_floor = lowest_floor
            self.direction = Direction.DOWN
        elif self.going_down and self.floor <= lowest_floor:
            self.target_floor = highest_floor
            self.direction = Direction.UP

        if self.target_floor <= -1 or self.target_floor >= self.max_floor:
            raise ElevatorError(f"Elevator is outside of bounds. Target: {self.target_floor}, max floor: {self.max_floor}")

        self.close_doors()
        self.floor += self.direction.value
        self.add_to_log(f"Elevator moving {self.direction.name} to {self.floor}")
        # Sleep added to simulate ticks. Purely for aesthetics
        time.sleep(0.5)


def generate_passengers(num_people: int, elevator: Elevator) -> list[Passenger]:
    total_population = []
    for _ in range(num_people):
        passenger = Passenger(elevator.max_floor)
        total_population.append(passenger)
        elevator.call_elevator(passenger.start_floor)

    return total_population


def simulate_elevator_usage(num_people: int, num_floors: int, capacity: int = 6) -> Elevator:
    elevator = Elevator(num_floors, capacity)
    total_population = generate_passengers(num_people, elevator)

    # Move elevator and onboard people
    while sum(elevator.floor_population) + len(elevator.elevator_population) > 0:
        for passenger in total_population:
            if passenger.in_elevator and passenger.arrived(elevator.floor):
                elevator.remove(passenger)

            if passenger.waiting():
                elevator.onboard(passenger)

        if sum(elevator.floor_population) + len(elevator.elevator_population) == 0:
            elevator.close_doors()
            elevator.direction = Direction.IDLE
            break

        elevator.move()
    elevator.add_to_log("All passengers arrived to their destination floors")

    return elevator


def run():
    num_people = 10
    num_floors = 5
    capacity = 4
    simulate_elevator_usage(num_people, num_floors, capacity)


if __name__ == "__main__":
    run()
