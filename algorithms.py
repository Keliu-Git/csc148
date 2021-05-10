"""CSC148 Assignment 1 - Algorithms

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module Description ===

This file contains two sets of algorithms: ones for generating new arrivals to
the simulation, and ones for making decisions about how elevators should move.

As with other files, you may not change any of the public behaviour (attributes,
methods) given in the starter code, but you can definitely add new attributes
and methods to complete your work here.

See the 'Arrival generation algorithms' and 'Elevator moving algorithsm'
sections of the assignment handout for a complete description of each algorithm
you are expected to implement in this file.
"""
import csv
from enum import Enum
import random
from typing import Dict, List, Optional

from entities import Person, Elevator


###############################################################################
# Arrival generation algorithms
###############################################################################
class ArrivalGenerator:
    """An algorithm for specifying arrivals at each round of the simulation.

    === Attributes ===
    max_floor: The maximum floor number for the building.
               Generated people should not have a starting or target floor
               beyond this floor.
    num_people: The number of people to generate, or None if this is left
                up to the algorithm itself.

    === Representation Invariants ===
    max_floor >= 2
    num_people is None or num_people >= 0
    """
    max_floor: int
    num_people: Optional[int]

    def __init__(self, max_floor: int, num_people: Optional[int]) -> None:
        """Initialize a new ArrivalGenerator.

        Preconditions:
            max_floor >= 2
            num_people is None or num_people >= 0
        """
        self.max_floor = max_floor
        if num_people is not None and num_people > max_floor:
            self.num_people = max_floor
        else:
            self.num_people = num_people

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        """Return the new arrivals for the simulation at the given round.

        The returned dictionary maps floor number to the people who
        arrived starting at that floor.

        You can choose whether to include floors where no people arrived.
        """
        raise NotImplementedError


class RandomArrivals(ArrivalGenerator):
    """Generate a fixed number of random people each round.

    Generate 0 people if self.num_people is None.

    For our testing purposes, this class *must* have the same initializer header
    as ArrivalGenerator. So if you choose to to override the initializer, make
    sure to keep the header the same!

    Hint: look up the 'sample' function from random.
    """

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        people = {}

        if self.num_people is not None:
            start_floors = random.sample(
                range(1, self.max_floor+1), self.num_people)
            target_floors = []
            for floor in start_floors:
                target = random.randint(1, self.max_floor)
                while target == floor:
                    target = random.randint(1, self.max_floor)
                target_floors.append(target)
            for i in range(len(start_floors)):
                if start_floors[i] in people:
                    people[start_floors[i]].append(
                        Person(start_floors[i], target_floors[i]))
                else:
                    people[start_floors[i]] = [Person(
                        start_floors[i], target_floors[i])]
        return people


class FileArrivals(ArrivalGenerator):
    """Generate arrivals from a CSV file.

    === Attributes ===
    arrival_sequence: a dictionary mapping round number to a list of
                      arrival data, where the even indices (0, 2, 4 ...) represent
                      the arrival floor number, and the odd indices (1, 3, 5 ...)
                      represent the target floor number.
    """
    arrival_sequence: Dict[int, List[int]]

    def __init__(self, max_floor: int, filename: str) -> None:
        """Initialize a new FileArrivals algorithm from the given file.

        The num_people attribute of every FileArrivals instance is set to None,
        since the number of arrivals depends on the given file.

        Precondition:
            <filename> refers to a valid CSV file, following the specified
            format and restrictions from the assignment handout.
        """
        ArrivalGenerator.__init__(self, max_floor, None)

        # We've provided some of the "reading from csv files" boilerplate code
        # for you to help you get started.

        self.arrival_sequence = {}
        with open(filename) as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                # to one line of the original file.
                # You'll need to convert the strings to ints and then process
                # and store them.
                int_list = []
                for item in line:
                    int_list.append(int(item))
                self.arrival_sequence[int_list[0]] = int_list[1:]

    def generate(self, round_num: int) -> Dict:
        """A method to generate new arrivals for each turn, based
        on the sequence provided by the file.
        """
        people = {}
        start_floor = []
        target_floor = []
        if round_num in self.arrival_sequence:
            sequence = self.arrival_sequence[round_num]
            for i in range(0, len(sequence), 2):
                start_floor.append(sequence[i])
                target_floor.append(sequence[i+1])

            for i in range(len(start_floor)):
                if start_floor[i] in people:
                    people[start_floor[i]].append(
                        Person(start_floor[i], target_floor[i]))
                else:
                    people[start_floor[i]] = [Person(
                        start_floor[i], target_floor[i])]

        return people


###############################################################################
# Elevator moving algorithms
###############################################################################
class Direction(Enum):
    """
    The following defines the possible directions an elevator can move.
    This is output by the simulation's algorithms.

    The possible values you'll use in your Python code are:
        Direction.UP, Direction.DOWN, Direction.STAY
    """
    UP = 1
    STAY = 0
    DOWN = -1


class MovingAlgorithm:
    """An algorithm to make decisions for moving an elevator at each round.
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """Return a list of directions for each elevator to move to.

        As input, this method receives the list of elevators in the simulation,
        a dictionary mapping floor number to a list of people waiting on
        that floor, and the maximum floor number in the simulation.

        Note that each returned direction should be valid:
            - An elevator at Floor 1 cannot move down.
            - An elevator at the top floor cannot move up.
        """
        raise NotImplementedError


class RandomAlgorithm(MovingAlgorithm):
    """A moving algorithm that picks a random direction for each elevator.
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """Return a list of random valid directions for each elevator.

        """
        output_directions = []
        for elevator in elevators:
            bad_direction = True
            while bad_direction:
                direction = random.randint(-1, 1)
                if direction == 0:
                    bad_direction = False
                    output_directions.append(Direction.STAY)
                elif direction == -1 and elevator.floor > 1:
                    bad_direction = False
                    elevator.floor -= 1
                    output_directions.append(Direction.DOWN)
                elif direction == 1 and elevator.floor < max_floor:
                    bad_direction = False
                    elevator.floor += 1
                    output_directions.append(Direction.UP)

        return output_directions


class PushyPassenger(MovingAlgorithm):
    """A moving algorithm that preferences the first passenger on each elevator.

    If the elevator is empty, it moves towards the *lowest* floor that has at
    least one person waiting, or stays still if there are no people waiting.

    If the elevator isn't empty, it moves towards the target floor of the
    *first* passenger who boarded the elevator.
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """ Return a list of directions based using the pushy passenger
            algorithm

        """
        output_directions = []
        for elevator in elevators:
            if len(elevator.passengers) == 0:
                floors = sorted(waiting)
                wait_on_floor = []
                for floor in floors:
                    if len(waiting[floor]) != 0:
                        wait_on_floor.append(floor)

                if len(wait_on_floor) == 0:
                    output_directions.append(Direction.STAY)
                else:
                    if wait_on_floor[0] < elevator.floor:
                        output_directions.append(Direction.DOWN)
                        elevator.floor -= 1

                    elif wait_on_floor[0] > elevator.floor:
                        output_directions.append(Direction.UP)
                        elevator.floor += 1
            else:
                first = elevator.passengers[0]
                if elevator.floor < first.target:
                    output_directions.append(Direction.UP)
                    elevator.floor += 1
                elif elevator.floor > first.target:
                    output_directions.append(Direction.DOWN)
                    elevator.floor -= 1

        return output_directions


class ShortSighted(MovingAlgorithm):
    """A moving algorithm that preferences the closest possible choice.

    If the elevator is empty, it moves towards the *closest* floor that has at
    least one person waiting, or stays still if there are no people waiting.

    If the elevator isn't empty, it moves towards the closest target floor of
    all passengers who are on the elevator.

    In this case, the order in which people boarded does *not* matter.
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """Return a list of directions for each elevators based
        on the ShortSighted algorithm
        """
        output_direction = []
        for elevator in elevators:
            if len(elevator.passengers) == 0:
                floors = sorted(waiting)
                wait_on_floor = []
                distance = []
                for floor in floors:
                    if len(waiting[floor]) != 0:
                        d = abs(elevator.floor - floor)
                        distance.append(d)
                        wait_on_floor.append(floor)

                if len(wait_on_floor) == 0:
                    output_direction.append(Direction.STAY)
                else:
                    lower = wait_on_floor[distance.index(min(distance))]
                    if lower < elevator.floor:
                        output_direction.append(Direction.DOWN)
                        elevator.floor -= 1

                    elif lower > elevator.floor:
                        output_direction.append(Direction.UP)
                        elevator.floor += 1
            else:
                floors = []
                distance = []
                for person in elevator.passengers:
                    d = abs(elevator.floor - person.target)
                    distance.append(d)
                    floors.append(person.target)

                min_floors = []
                for floor in floors:
                    if abs(elevator.floor - floor) == min(distance):
                        min_floors.append(floor)
                lower = min_floors[0]
                for floor in min_floors:
                    if floor < lower:
                        lower = floor

                if lower < elevator.floor:
                    output_direction.append(Direction.DOWN)
                    elevator.floor -= 1

                elif lower > elevator.floor:
                    output_direction.append(Direction.UP)
                    elevator.floor += 1

        return output_direction


if __name__ == '__main__':
    # Don't forget to check your work regularly with python_ta!
    import python_ta
    python_ta.check_all(config={
        'allowed-io': ['__init__'],
        'extra-imports': ['entities', 'random', 'csv', 'enum'],
        'max-nested-blocks': 4,
        'disable': ['R0201']
    })
