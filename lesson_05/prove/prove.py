"""
Course: CSE 251 
Lesson: L05 Prove
File:   prove.py
Author: <Tyler Bartle>

Purpose: Assignment 05 - Factories and Dealers

Instructions:

- Read the comments in the following code.  
- Implement your code where the TODO comments are found.
- No global variables, all data must be passed to the objects.
- Only the included/imported packages are allowed.  
- Thread/process pools are not allowed
- You MUST use a barrier!
- Do not use try...except statements.
- You are not allowed to use the normal Python Queue object. You must use Queue251.
- The shared queue between the threads that are used to hold the Car objects
  can not be greater than MAX_QUEUE_SIZE.

I feel like I met the requirements for this assignment.
I successfully implemented the required number of factories and dealers, 
    and the barrier to signal the end of production.
The code is also not very different than last week's assignment,
    proving that I (hopefully) did it correctly.
"""

from datetime import datetime, timedelta
import time
import threading
import random

# Include cse 251 common Python files
from cse251 import *

# Global Constants.
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
        self.__max_size = 0

    def get_max_size(self):
        return self.__max_size

    def put(self, item):
        self.__items.append(item)
        if len(self.__items) > self.__max_size:
            self.__max_size = len(self.__items)

    def get(self):
        return self.__items.pop(0)


class Factory(threading.Thread):
    """ This is a factory.  It will create cars and place them on the car queue """

    def __init__(self, queue, space_available, cars_available, barrier, log, dealer_count):
        self.cars_to_produce = random.randint(200, 300) # DO NOT change
        super().__init__()
        self.queue = queue
        self.space_available = space_available
        self.cars_available = cars_available
        self.barrier = barrier
        self.log = log
        self.dealer_count = dealer_count


    def run(self):
        # TODO produce the cars, the send them to the dealerships

        # TODO wait until all of the factories are finished producing cars

        # TODO "Wake up/signal" the dealerships one more time.  Select one factory to do this
        for _ in range(self.cars_to_produce):
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
        # Signal the dealer that there there are not more cars
        # self.log.write("Factory: Production complete!")
        leader = self.barrier.wait()
        if leader == 0:
            for _ in range(self.dealer_count):
                self.space_available.acquire()
                self.queue.put("bye forever")
                self.cars_available.release()



class Dealer(threading.Thread):
    """ This is a dealer that receives cars """

    def __init__(self, queue, space_available, cars_available, log):
        # TODO, you need to add arguments that pass all of data that 1 Dealer needs
        # to sell a car
        super().__init__()
        self.queue = queue
        self.space_available = space_available
        self.cars_available = cars_available
        self.log = log
        self.cars_sold = 0

    def run(self):
        while True:
            # TODO handle a car
            """
            take the car from the queue
            signal the factory that there is an empty slot in the queue
            """
            self.cars_available.acquire()  # Wait for a car to be available
            c = self.queue.get()  # Get the car from the queue
            self.space_available.release()
            if c == "bye forever":
                # self.log.write("Dealer: Received termination signal.")
                break
            self.cars_sold += 1
            # Sleep a little - don't change.  This is the last line of the loop
            time.sleep(random.random() / (SLEEP_REDUCE_FACTOR + 0))



def run_production(factory_count, dealer_count):
    """ This function will do a production run with the number of
        factories and dealerships passed in as arguments.
    """

    # TODO Create semaphore(s) if needed
    # TODO Create queue
    # TODO Create lock(s) if needed
    # TODO Create barrier

    space_available = threading.Semaphore(MAX_QUEUE_SIZE)  # Starts with MAX_QUEUE_SIZE spaces
    cars_available = threading.Semaphore(0)  # Starts with 0 cars available
    car_queue = Queue251()
    barrier = threading.Barrier(factory_count)

    # This is used to track the number of cars received by each dealer
    # dealer_stats = list([0] * dealer_count)
    dealer_stats = []

    # TODO create your factories, each factory will create a random amount of cars; your code must account for this.
    # NOTE: You have no control over how many cars a factory will create in this assignment.
    factories = [Factory(car_queue, space_available, cars_available, barrier, log, dealer_count) for _ in range(factory_count)]
    # TODO create your dealerships
    dealers   = [Dealer(car_queue, space_available, cars_available, log) for _ in range(dealer_count)]
    log.start_timer()

    # TODO Start all dealerships
    for d in dealers:
        d.start()
    # TODO Start all factories
    for f in factories:
        f.start()
            
    # This is used to track the number of cars produced by each factory NOTE: DO NOT pass this into
    # your factories! You must collect this data here in `run_production` after the factories are finished.
    factory_stats = []

    # TODO Wait for the factories and dealerships to complete; do not forget to get the factories stats
    for f in factories:
        f.join()
        factory_stats.append(f.cars_to_produce)
    for d in dealers:
        d.join()
        dealer_stats.append(d.cars_sold)
    run_time = log.stop_timer(f'{sum(dealer_stats)} cars have been created.')

    # This function must return the following - Don't change!
    # factory_stats: is a list of the number of cars produced by each factory.
    #                collect this information after the factories are finished. 
    return (run_time, car_queue.get_max_size(), dealer_stats, factory_stats)


def main(log):
    """ Main function - DO NOT CHANGE! """

    runs = [(1, 1), (1, 2), (2, 1), (2, 2), (2, 5), (5, 2), (10, 10)]
    for factories, dealerships in runs:
        run_time, max_queue_size, dealer_stats, factory_stats = run_production(factories, dealerships)

        log.write(f'Factories      : {factories}')
        log.write(f'Dealerships    : {dealerships}')
        log.write(f'Run Time       : {run_time:.4f}')
        log.write(f'Max queue size : {max_queue_size}')
        log.write(f'Factory Stats  : Made = {sum(dealer_stats)} @ {factory_stats}')
        log.write(f'Dealer Stats   : Sold = {sum(factory_stats)} @ {dealer_stats}')
        log.write('')

        # The number of cars produces needs to match the cars sold
        assert sum(dealer_stats) == sum(factory_stats)


if __name__ == '__main__':
    log = Log(show_terminal=True)
    main(log)

