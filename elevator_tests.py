import pytest

from elevator import Direction, Elevator, ElevatorError, Passenger, generate_passengers, simulate_elevator_usage


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda x: None)


class TestPassenger:
    @pytest.mark.parametrize("floors", [2, 5, 10])
    def test_passenger_creation(self, floors):
        passenger = Passenger(floors)
        assert passenger.start_floor in range(floors)
        assert passenger.target_floor in range(floors)
        assert passenger.start_floor != passenger.target_floor
        assert passenger.direction in [Direction.UP, Direction.DOWN]

    def test_passenger_waiting(self):
        passenger = Passenger(5)
        assert passenger.waiting() is True
        passenger.in_elevator = True
        assert passenger.waiting() is False

    def test_passenger_arrived(self):
        passenger = Passenger(5)
        passenger.target_floor = 2
        assert passenger.arrived(2) is True

    def test_generate_passengers(self):
        passengers_count = 5
        elevator = Elevator(max_floor=10, capacity=8)
        passengers_list = generate_passengers(passengers_count, elevator)
        assert len(passengers_list) == passengers_count
        assert isinstance(passengers_list[0], Passenger)


class TestElevator:
    def test_elevator_initialization(self):
        elevator = Elevator(max_floor=10, capacity=8)
        assert elevator.floor == 0
        assert elevator.direction == Direction.IDLE
        assert elevator.capacity == 8
        assert elevator.elevator_population == []

    def test_elevator_open_close_doors(self):
        elevator = Elevator(5)
        assert elevator.doors_opened is False
        elevator.open_doors()
        assert elevator.doors_opened is True
        elevator.close_doors()
        assert elevator.doors_opened is False

    def test_elevator_is_full(self):
        elevator = Elevator(5, capacity=2)
        elevator.onboard(Passenger(5, start_floor=0))
        elevator.onboard(Passenger(5, start_floor=0))
        passenger = Passenger(5, start_floor=0)
        elevator.onboard(passenger)
        assert elevator.is_full
        assert elevator.log[-1] == f"Elevator is full. Passenger {passenger.id} needs to wait."

    def test_elevator_remove(self):
        elevator = Elevator(5)
        passenger = Passenger(5, start_floor=0, target_floor=1)
        elevator.onboard(passenger)
        elevator.move()
        elevator.remove(passenger)
        assert passenger.in_elevator is False
        assert passenger.finished is True
        assert passenger not in elevator.elevator_population
        assert f"Passenger {passenger.start_floor} -> {passenger.target_floor} exited at floor {elevator.floor}" in elevator.log

    def test_cant_remove(self):
        elevator = Elevator(5)
        passenger = Passenger(5, start_floor=0, target_floor=1)
        elevator.onboard(passenger)
        elevator.remove(passenger)
        assert passenger.in_elevator is True
        assert passenger.finished is False
        assert f"Passenger {passenger.start_floor} -> {passenger.target_floor} exited at floor {elevator.floor}" not in elevator.log

    def test_onboard_passenger_from_other_floor(self):
        elevator = Elevator(5)
        passenger = Passenger(5, start_floor=2)
        elevator.call_elevator(passenger.start_floor)

        elevator.onboard(passenger)
        assert passenger.in_elevator is False
        assert elevator.floor_population[passenger.start_floor] == 1
        assert len(elevator.elevator_population) == 0

    def test_move(self):
        elevator = Elevator(5)
        passenger = Passenger(5, start_floor=0, target_floor=1)
        assert elevator.floor == 0
        elevator.onboard(passenger)
        elevator.move()
        assert elevator.floor == 1

    def test_move_fail(self):
        elevator = Elevator(5)
        assert elevator.floor == 0
        with pytest.raises(ElevatorError) as exc_info:
            elevator.move()
        assert str(exc_info.value) == "Elevator is moving, but no buttons pressed"

    def test_elevator_call_onboard_move(self):
        elevator = Elevator(5)
        passenger1 = Passenger(5, start_floor=0, target_floor=2)
        passenger2 = Passenger(5, start_floor=3, target_floor=2)
        passenger3 = Passenger(5, start_floor=4, target_floor=1)
        elevator.call_elevator(passenger1.start_floor)
        elevator.call_elevator(passenger2.start_floor)
        elevator.call_elevator(passenger3.start_floor)
        assert elevator.floor_population[passenger1.start_floor] == 1

        elevator.onboard(passenger1)
        assert passenger1.in_elevator is True
        assert elevator.floor_population[passenger1.start_floor] == 0
        assert len(elevator.elevator_population) == 1

        elevator.move()
        assert elevator.floor == 1
        assert elevator.direction == Direction.UP
        assert elevator.doors_opened is False

        elevator.move()
        assert elevator.doors_opened is False
        elevator.remove(passenger1)
        assert elevator.floor == 2
        assert elevator.direction == Direction.UP
        assert elevator.doors_opened is True
        assert len(elevator.elevator_population) == 0

        elevator.move()
        assert elevator.floor == 3
        assert elevator.direction == Direction.UP

        elevator.move()
        elevator.onboard(passenger3)
        assert elevator.floor == 4
        assert passenger3.in_elevator is True
        assert len(elevator.elevator_population) == 1
        assert passenger3.start_floor not in elevator.floor_population

        elevator.move()
        elevator.onboard(passenger2)
        assert elevator.floor == 3
        assert elevator.direction == Direction.DOWN

        elevator.move()
        elevator.remove(passenger2)
        assert elevator.floor == 2
        assert elevator.direction == Direction.DOWN
        assert passenger2.finished is True

        elevator.move()
        elevator.remove(passenger3)
        elevator.direction = Direction.IDLE
        assert elevator.floor == 1
        assert elevator.direction == Direction.IDLE
        assert elevator.doors_opened is True
        assert len(elevator.elevator_population) == 0
        assert elevator.floor_population[1] == 0
        assert elevator.floor_population[2] == 0

    @pytest.mark.parametrize(
        "number_of_passengers, max_floor, capacity",
        [
            (3, 5, 2),
            (5, 7, 4),
            (10, 15, 4),
            (16, 5, 4),
            (100, 10, 8),
            (1000, 10, 8),
        ]
    )
    def test_simulate_random_elevator_usage(self, number_of_passengers, max_floor, capacity):
        elevator = simulate_elevator_usage(number_of_passengers, max_floor, capacity)
        joined_log = "\n".join(elevator.log).lower()

        assert joined_log.count("entered") == joined_log.count("exited")
        assert joined_log.count("opened") == joined_log.count("closed")

    def test_zero_passengers(self):
        number_of_passengers = 0
        max_floor = 4
        elevator = simulate_elevator_usage(number_of_passengers, max_floor)

        assert len(elevator.log) == 1

    def test_one_floor(self):
        number_of_passengers = 5
        max_floor = 1
        with pytest.raises(ValueError) as exc_info:
            simulate_elevator_usage(number_of_passengers, max_floor)

        assert str(exc_info.value) == "Floors count must be more than 1"
