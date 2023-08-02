# Elevator Control System

This application simulates the movement of a single elevator and handles passenger requests from different floors.

## Requirements

* Python 3.x

## Setup

To setup, you need to create a virtual environment first and activate it

```
cd /path/to/elevator-service
virtualenv venv
source venv/bin/activate
```

Then, you need to install the dependencies

```
pip install -r requirements.txt
```

## Execution
To execute the code run the following command:

```
python elevator.py
```

The simulation will start, and you will see logs describing the elevator's movement, passenger boarding, and exits. The code simulates the elevator movement for a predefined number of passengers and floors. You can adjust the number of passengers and floors in the `run()` function.


## Tests

Unit tests for the Elevator and Passenger classes are implemented using pytest.

To run the tests, execute the following command in the project directory:

```
pytest elevator_tests.py 
```


To see the test code coverage execute the following command:

```
pytest --cov=elevator elevator_tests.py 
```

To check the covered lines run:

```
coverage html
```

Then open `./htmlcov/index.html` from your browser



