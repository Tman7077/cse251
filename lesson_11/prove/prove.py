"""
Course: CSE 251
Lesson Week: 11
File: Assignment.py

Author: <Tyler Bartle>

Justification for grade:
- I have completed the assignment as per the requirements.
- I have added comments to explain the code.
- I have tested the code and it runs without errors.
- While not technically required per the instructions,
    the room is always cleaned in between parties (becuase that makes sense).
"""

import time
import random
import multiprocessing as mp

# number of cleaning staff and hotel guests
CLEANING_STAFF = 2
HOTEL_GUESTS = 5

# Run program for this number of seconds
TIME = 60

STARTING_PARTY_MESSAGE =  'Turning on the lights for the party vvvvvvvvvvvvvv'
STOPPING_PARTY_MESSAGE  = 'Turning off the lights  ^^^^^^^^^^^^^^^^^^^^^^^^^^'

STARTING_CLEANING_MESSAGE =  'Starting to clean the room >>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
STOPPING_CLEANING_MESSAGE  = 'Finish cleaning the room <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'

def cleaner_waiting(id):
    print(f'Cleaner: {id} waiting...')
    time.sleep(random.uniform(0, 2))

def cleaner_cleaning(id):
    print(f'Cleaner: {id}')
    time.sleep(random.uniform(0, 2))

def guest_waiting(id):
    print(f'Guest: {id} waiting...')
    time.sleep(random.uniform(0, 2))

def guest_partying(id, count):
    print(f'Guest: {id}, count = {count}')
    time.sleep(random.uniform(0, 1))

def cleaner(id, room_empty, cleaned_count):
    """
    do the following for TIME seconds
        cleaner will wait to try to clean the room (cleaner_waiting())
        get access to the room
        display message STARTING_CLEANING_MESSAGE
        Take some time cleaning (cleaner_cleaning())
        display message STOPPING_CLEANING_MESSAGE
    """
    end_time = time.time() + TIME
    while time.time() < end_time:
        cleaner_waiting(id)
        room_empty.acquire()  # Wait until no guests are in the room.
        print(STARTING_CLEANING_MESSAGE)
        cleaner_cleaning(id)
        print(STOPPING_CLEANING_MESSAGE)
        cleaned_count.value += 1
        room_empty.release()  # Allow guests to enter.

def guest(id, room_empty, guest_lock, guest_count, party_count, guest_semaphore):
    """
    do the following for TIME seconds
        guest will wait to try to get access to the room (guest_waiting())
        get access to the room
        display message STARTING_PARTY_MESSAGE if this guest is the first one in the room
        Take some time partying (call guest_partying())
        display message STOPPING_PARTY_MESSAGE if the guest is the last one leaving in the room
    """
    end_time = time.time() + TIME
    while time.time() < end_time:
        guest_waiting(id)
        guest_semaphore.acquire()  # Limit the number of guests that can be partying.
        
        # Begin critical section to update guest count.
        with guest_lock:
            guest_count.value += 1
            if guest_count.value == 1:
                room_empty.acquire()  # First guest blocks the cleaners.
                print(STARTING_PARTY_MESSAGE)
                party_count.value += 1
        # End critical section.
        
        guest_partying(id, guest_count.value)
        
        # Begin critical section for leaving.
        with guest_lock:
            guest_count.value -= 1
            if guest_count.value == 0:
                print(STOPPING_PARTY_MESSAGE)
                room_empty.release()  # Last guest leaves and allows cleaners in.
        # End critical section.
        
        guest_semaphore.release()

def main():
    # Start time of the running of the program. 
    start_time = time.time()

    # TODO - add any variables, data structures, processes you need
    room_empty = mp.Semaphore(1) # Acts as a mutex for cleaning (only available when room is empty)
    guest_lock = mp.Lock()       # Protects guest_count updates.
    cleaned_count = mp.Value('i', 0)
    guest_count = mp.Value('i', 0)
    party_count = mp.Value('i', 0)
    guest_semaphore = mp.Semaphore(HOTEL_GUESTS)
    # TODO - add any arguments to cleaner() and guest() that you need
    cleaners = [mp.Process(target=cleaner, args=(i, room_empty, cleaned_count)) for i in range(CLEANING_STAFF)]
    for c in cleaners:
        c.start()

    guests = [mp.Process(target=guest, args=(i, room_empty, guest_lock, guest_count, party_count, guest_semaphore)) for i in range(HOTEL_GUESTS)]
    for g in guests:
        g.start()

    for c in cleaners:
        c.join()
    for g in guests:
        g.join()

    # Results
    print(f'Room was cleaned {cleaned_count.value} times, there were {party_count.value} parties')


if __name__ == '__main__':
    main()

