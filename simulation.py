"""CSC148 Assignment 1 - Simulation

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module description ===
This contains the main Simulation class that is actually responsible for
creating and running the simulation. You'll also find the function `sample_run`
here at the bottom of the file, which you can use as a starting point to run
your simulation on a small configuration.

Note that we have provided a fairly comprehensive list of attributes for
Simulation already. You may add your own *private* attributes, but should not
remove any of the existing attributes.
"""
# You may import more things from these modules (e.g., additional types from
# typing), but you may not import from any other modules.
from typing import Dict, List, Any

import algorithms
from entities import Person, Elevator
from visualizer import Visualizer


class Simulation:
    """The main simulation class.

    === Attributes ===
    arrival_generator: the algorithm used to generate new arrivals.
    elevators: a list of the elevators in the simulation
    moving_algorithm: the algorithm used to decide how to move elevators
    num_floors: the number of floors
    visualizer: the Pygame visualizer used to visualize this simulation
    waiting: a dictionary of people waiting for an elevator
             (keys are floor numbers, values are the list of waiting people)
    tot_time_people: a dictionary that maps the total number of people
                    generated to a list of time it takes for each passenger
                    to complete their trip.
    """
    arrival_generator: algorithms.ArrivalGenerator
    elevators: List[Elevator]
    moving_algorithm: algorithms.MovingAlgorithm
    num_floors: int
    visualizer: Visualizer
    waiting: Dict[int, List[Person]]
    tot_time_people: List[Any]

    def __init__(self,
                 config: Dict[str, Any]) -> None:
        """Initialize a new simulation using the given configuration."""

        self.arrival_generator = config['arrival_generator']

        self.elevators = [None]*config['num_elevators']
        for index in range(config['num_elevators']):
            self.elevators[index] = Elevator(config['elevator_capacity'])

        self.num_floors = config['num_floors']
        self.moving_algorithm = config['moving_algorithm']
        self.waiting = {}
        self.tot_time_people = [0, []]

        # Initialize the visualizer.
        # Note that this should be called *after* the other attributes
        # have been initialized.
        self.visualizer = Visualizer(self.elevators,
                                     self.num_floors,
                                     config['visualize'])

    ############################################################################
    # Handle rounds of simulation.
    ############################################################################
    def run(self, num_rounds: int) -> Dict[str, Any]:
        """Run the simulation for the given number of rounds.

        Return a set of statistics for this simulation run, as specified in the
        assignment handout.

        Precondition: num_rounds >= 1.

        Note: each run of the simulation starts from the same initial state
        (no people, all elevators are empty and start at floor 1).
        """
        for i in range(num_rounds):
            self.visualizer.render_header(i)

            # Stage 1: generate new arrivals
            self._generate_arrivals(i)

            # Stage 2: leave elevators
            self._handle_leaving()

            # Stage 3: board elevators
            self._handle_boarding()

            # Stage 4: move the elevators using the moving algorithm
            self._move_elevators()

            # Pause for 1 second
            self.visualizer.wait(1)

            # Update the time that each person has waited
            # For people waiting
            for key in self.waiting:
                people = self.waiting.get(key)
                for person in people:
                    person.wait_time_increment()

            # For people in elevators
            for elevator in self.elevators:
                for person in elevator.passengers:
                    person.wait_time_increment()

        return self._calculate_stats(num_rounds)

    def _generate_arrivals(self, round_num: int) -> None:
        """Generate and visualize new arrivals."""

        new_arrivals = self.arrival_generator.generate(round_num+1)
        self.waiting.update(self.same_floor_arrival(new_arrivals))

        if self.waiting is not None:
            Visualizer.show_arrivals(self.visualizer, self.waiting)

    def same_floor_arrival(self, new_arrivals: Dict) -> Dict:
        """ Add to the list of people that is already waiting on a
        specific floor

        """
        same_floor = []
        for key in new_arrivals:
            self.tot_time_people[0] = self.tot_time_people[0] + 1

            if key in self.waiting:
                self.waiting[key].extend(new_arrivals[key])
                same_floor.append(key)
        for key in same_floor:
            del new_arrivals[key]
        return new_arrivals

    def _handle_leaving(self) -> None:
        """Handle people leaving elevators."""
        for elevator in self.elevators:
            for person in elevator.passengers:
                if person.target == elevator.floor and \
                        (isinstance(self.moving_algorithm,
                                    algorithms.RandomAlgorithm) or
                         isinstance(self.moving_algorithm,
                                    algorithms.ShortSighted)):

                    assert person.target == elevator.floor
                    self._passenger_leaves(elevator, person)

                elif isinstance(self.moving_algorithm,
                                algorithms.PushyPassenger):

                    first = elevator.passengers[0]
                    if first is person and \
                            first.target == elevator.floor:
                        self._passenger_leaves(elevator, person)

    def _passenger_leaves(self, elevator: Elevator, person: Person) -> None:
        self.tot_time_people[1].append(person.wait_time)
        index = elevator.passengers.index(person)
        del elevator.passengers[index]
        Visualizer.show_disembarking(self.visualizer,
                                     person,
                                     elevator)

    def _handle_boarding(self) -> None:
        """Handle boarding of people and visualize."""
        for elevator in self.elevators:
            if elevator.floor in self.waiting:
                while elevator.fullness() < 1.0 and \
                        len(self.waiting[elevator.floor]) > 0:
                    self._board_passenger(elevator)

    def _board_passenger(self, elevator: Elevator) -> None:
        """Helper method to self._handle_boarding.
        Boards the passengers onto the elevator
        """
        people = self.waiting.get(elevator.floor)
        for person in people:
            if person is not None:
                elevator.append_passenger(person)
                Visualizer.show_boarding(self.visualizer,
                                         person,
                                         elevator)
                del people[people.index(person)]

    def _move_elevators(self) -> None:
        """Move the elevators in this simulation.

        Use this simulation's moving algorithm to move the elevators.
        """
        if isinstance(self.moving_algorithm, algorithms.RandomAlgorithm):
            move_sequence = algorithms.RandomAlgorithm.move_elevators\
                (self.moving_algorithm,
                 self.elevators,
                 self.waiting,
                 self.num_floors)

        elif isinstance(self.moving_algorithm, algorithms.PushyPassenger):
            move_sequence = algorithms.PushyPassenger.move_elevators\
                (self.moving_algorithm,
                 self.elevators,
                 self.waiting,
                 self.num_floors)

        elif isinstance(self.moving_algorithm, algorithms.ShortSighted):
            move_sequence = algorithms.ShortSighted.move_elevators\
                (self.moving_algorithm,
                 self.elevators,
                 self.waiting,
                 self.num_floors)

        Visualizer.show_elevator_moves(self.visualizer,
                                       self.elevators,
                                       move_sequence)

    ############################################################################
    # Statistics calculations
    ############################################################################
    def _calculate_stats(self, iterations: int) -> Dict[str, int]:
        """Report the statistics for the current run of this simulation.
        """
        tot_people = self.tot_time_people[0]
        time_lst = self.tot_time_people[1]
        tot_completed = len(time_lst)
        max_time = 0
        min_time = time_lst[0]
        tot_time = 0
        for time in time_lst:
            if time > max_time:
                max_time = time
            if time < min_time:
                min_time = time
            tot_time += time
        avg_time = tot_time/tot_completed

        return {
            'num_iterations': iterations,
            'total_people': tot_people,
            'people_completed': tot_completed,
            'max_time': max_time,
            'min_time': min_time,
            'avg_time': avg_time
        }


def sample_run() -> Dict[str, int]:
    """Run a sample simulation, and return the simulation statistics."""
    config = {
         'num_floors': 6,
         'num_elevators': 6,
         'elevator_capacity': 3,
         'num_people_per_round': 2,
         # Random arrival generator with 6 max floors and 2 arrivals per round.
         'arrival_generator': algorithms.RandomArrivals(6, 1),
         'moving_algorithm': algorithms.ShortSighted(),
         'visualize': True
    }
    
    sim = Simulation(config)
    stats = sim.run(15)
    return stats
'''
    config = {
        'num_floors': 5,
        'num_elevators': 2,
        'elevator_capacity': 1,
        # This is likely not used.
        'num_people_per_round': 2,
        'arrival_generator': algorithms.FileArrivals(5, 'sample_arrivals.csv'),
        'moving_algorithm': algorithms.ShortSighted(),
        'visualize': True
    }
    sim = Simulation(config)
    stats = sim.run(10)
    '''




if __name__ == '__main__':
    # Uncomment this line to run our sample simulation (and print the
    # statistics generated by the simulation).
    print(sample_run())

    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['entities', 'visualizer', 'algorithms', 'time'],
        'max-nested-blocks': 4
    })
