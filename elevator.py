from enum import Enum


class Status(Enum):
    IDLE = "idle"
    UP = "up"
    DOWN = "down"


class Elevator:
    def __init__(self):
        self.status = Status.IDLE


if __name__ == "__main__":
    pass
