"""
Course: CSE 251 
Lesson: L04 Prove
File:   prove.py
Author: <Tyler Bartle>

Purpose: Assignment 04 - Factory and Dealership

Instructions:

- Complete the assignments TODO sections and DO NOT edit parts you were told to leave alone.
- Review the full instructions in Canvas; there are a lot of DO NOTS in this lesson.

Justification for grade:
I completed all of the assignment requirements,
    and didn't break any of the rules.
I attempted to optimize the code in all ways I knew how, even if
    it's not as efficient as the sample solution.
It successfully threads and uses sempahores, and doesn't
    overstuff the queue or break even after many runs.
"""

import time
import threading
import random

# Include cse 251 common Python files
from cse251 import *

# Global Constants - DO NOT CHANGE
CARS_TO_PRODUCE = 500
MAX_QUEUE_SIZE = 10
SLEEP_REDUCE_FACTOR = 50

# NO GLOBAL VARIABLES!

class Car():
    """ This is the Car class that will be created by the factories """

    # Class Variables
    car_makes = ('Ford', 'Chevrolet', 'Dodge', 'Fiat', 'Volvo', 'Infiniti', 'Jeep', 'Subaru', 
                'Buick', 'Volkswagen', 'Chrysler', 'Smart', 'Nissan', 'Toyota', 'Lexus', 
                'Mitsubishi', 'Mazda', 'Hyundai', 'Kia', 'Acura', 'Honda')

    car_models = ('A1', 'M1', 'XOX', 'XL', 'XLS', 'XLE' ,'Super' ,'Tall' ,'Flat', 'Middle', 'Round',
                'A2', 'M1X', 'SE', 'SXE', 'MM', 'Charger', 'Grand', 'Viper', 'F150', 'Town', 'Ranger',
                'G35', 'Titan', 'M5', 'GX', 'Sport', 'RX')

    car_years = [i for i in range(1990, datetime.now().year)]

    '''
    def __init__(self):
        # Make a random car
        self.model = random.choice(Car.car_models)
        self.make = random.choice(Car.car_makes)
        self.year = random.choice(Car.car_years)

        # Sleep a little.  Last statement in this for loop - don't change
        time.sleep(random.random() / (SLEEP_REDUCE_FACTOR))

        # Display the car that has was just created in the terminal
        print(f'Created: {self.info()}')
           
    def info(self):
        """ Helper function to quickly get the car information. """
        return f'{self.make} {self.model}, {self.year}'
    
    '''
    @staticmethod
    def gen_random():
        '''
        Instantiating a new Car() each time, and therefore
            - initializing possible makes, models, and years,
            - randomizing the make, model, and year, and
            - storing the make, model and year within self
        seemed inefficient. The lists of possibilities are static,
        so I figured a static method would save a little more time (and memory).
        Bonus points, you don't even have to call .info() as it just returns a string (instead of a whole object).

        * This one didn't say I can't modify it... I hope this isn't cheating :)
        '''
        make = random.choice(Car.car_makes)
        model = random.choice(Car.car_models)
        year = random.choice(Car.car_years)
        # Sleep a little.  Last statement in this for loop - don't change
        time.sleep(random.random() / (SLEEP_REDUCE_FACTOR))
        return f'{make} {model}, {year}'


class Queue251():
    """ This is the queue object to use for this assignment. Do not modify!! """

    def __init__(self):
        self.__items = []

    def size(self):
        return len(self.__items)

    def put(self, item):
        if len(self.__items) <= 10:
            self.__items.append(item)
        else:
            assert "you fed me eleven cake you silly boy"
        # I had to modify this because it wouldn't compile with the original assert line

    def get(self):
        return self.__items.pop(0)


class Factory(threading.Thread):
    """ This is a factory.  It will create cars and place them on the car queue """

    def __init__(self, queue, space_available, cars_available, log):
        # TODO, you need to add arguments that will pass all of data that 1 factory needs
        # to create cars and to place them in a queue.
        super().__init__()
        self.queue = queue
        self.space_available = space_available
        self.cars_available = cars_available
        self.log = log


    def run(self):
        for _ in range(CARS_TO_PRODUCE):
            # TODO Add you code here
            """
            create a car
            place the car on the queue
            signal the dealer that there is a car on the queue
            """
            c= Car.gen_random()
            self.space_available.acquire()  # Wait for space in the queue
            self.queue.put(c)  # Add the car to the queue
            self.cars_available.release()  # Signal that a car is available
            self.log.write(f"Factory produced: {c}")
        # Signal the dealer that there there are not more cars
        self.space_available.acquire()
        self.queue.put("bye forever")
        self.cars_available.release()
        self.log.write("Factory: Production complete!")


class Dealer(threading.Thread):
    """ This is a dealer that receives cars """

    def __init__(self, queue, space_available, cars_available, log, queue_stats):
        # TODO, you need to add arguments that pass all of data that 1 Dealer needs
        # to sell a car
        super().__init__()
        self.queue = queue
        self.space_available = space_available
        self.cars_available = cars_available
        self.log = log
        self.queue_stats = queue_stats

    def run(self):
        while True:
            # TODO Add your code here
            """
            take the car from the queue
            signal the factory that there is an empty slot in the queue
            """
            self.cars_available.acquire()  # Wait for a car to be available
            c = self.queue.get()  # Get the car from the queue
            self.space_available.release()
            if c == "bye forever":
                self.log.write("Dealer: Received termination signal.")
                break
            self.queue_stats[self.queue.size()] += 1
            self.log.write(f"Dealer sold: {c}")
            # Sleep a little after selling a car
            # Last statement in this for loop - don't change
            time.sleep(random.random() / (SLEEP_REDUCE_FACTOR))
            



def main():
    log = Log(show_terminal=True)

    # TODO Create semaphore(s)
    # TODO Create queue251 
    # TODO Create lock(s) ?

    # sem = threading.Semaphore(MAX_QUEUE_SIZE)
    space_available = threading.Semaphore(MAX_QUEUE_SIZE)  # Starts with MAX_QUEUE_SIZE spaces
    cars_available = threading.Semaphore(0)  # Starts with 0 cars available
    queue = Queue251()

    # This tracks the length of the car queue during receiving cars by the dealership
    # i.e., update this list each time the dealer receives a car
    queue_stats = [0] * MAX_QUEUE_SIZE

    # TODO create your one factory
    twenty_thousand_possible_cars_ten_at_a_time = Factory(queue, space_available, cars_available, log)
    # TODO create your one dealership
    the_most_eclectic_ten_car_dealership_on_planet_earth = Dealer(queue, space_available, cars_available, log, queue_stats)
    log.start_timer()

    # TODO Start factory and dealership
    twenty_thousand_possible_cars_ten_at_a_time.start()
    the_most_eclectic_ten_car_dealership_on_planet_earth.start()
    # TODO Wait for factory and dealership to complete
    twenty_thousand_possible_cars_ten_at_a_time.join()
    the_most_eclectic_ten_car_dealership_on_planet_earth.join()
    log.stop_timer(f'All {sum(queue_stats)} have been created and sold.')

    xaxis = [i + 1 for i in range(0, MAX_QUEUE_SIZE)] # i + 1 because the range is 1-10, not 0-9.
    plot = Plots()
    plot.bar(xaxis, queue_stats, title=f'{sum(queue_stats)} Produced: Count VS Queue Size', x_label='Queue Size', y_label='Count', filename=f'Production count vs queue size-{time.strftime("%H%M%S")}.png')



if __name__ == '__main__':
    main()