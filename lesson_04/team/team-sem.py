"""
Course: CSE 251 
Lesson: L04 Team Activity
File:   team.py
Author: <Tyler Bartle>

Purpose: Practice concepts of Queues, Locks, and Semaphores.

Instructions:

- Review instructions in Canvas.

Question:

- Is the Python Queue thread safe? (https://en.wikipedia.org/wiki/Thread_safety)
"""

import threading
import queue
import requests
import json

# Include cse 251 common Python files
from cse251 import *

RETRIEVE_THREADS = 4        # Number of retrieve_threads, 38 is length of urls list and goes fastest
NO_MORE_VALUES = 'No more'  # Special value to indicate no more items in the queue

def retrieve_thread(q, s, l):  # TODO add arguments
    """ Process values from the data_queue """

    while True:
        # TODO check to see if anything is in the queue
        s.acquire()
        # TODO process the value retrieved from the queue
        url = q.get()
        s.release()
        if url == NO_MORE_VALUES:
            break
        # TODO make Internet call to get characters name and log it
        response = requests.get(url).json()
        l.write(response['name'])



def file_reader(q, l): # TODO add arguments
    """ This thread reading the data file and places the values in the data_queue """

    # TODO Open the data file "urls.txt" and place items into a queue
    with open("urls.txt", "r") as file:
        for line in file:
            q.put(line.strip())
    l.write('finished reading file')

    # TODO signal the retrieve threads one more time that there are "no more values"
    for _ in range(RETRIEVE_THREADS):
        q.put(NO_MORE_VALUES)


def main():
    """ Main function """

    log = Log(show_terminal=True)

    # TODO create queue
    # TODO create semaphore (if needed)

    q = queue.Queue()
    s = threading.Semaphore(RETRIEVE_THREADS)

    # TODO create the threads. 1 filereader() and RETRIEVE_THREADS retrieve_thread()s
    # Pass any arguments to these thread need to do their job

    fr = threading.Thread(target=file_reader, args=(q,log))
    
    rts = []
    for _ in range(RETRIEVE_THREADS):
        rts.append(threading.Thread(target=retrieve_thread, args=(q, s, log)))

    log.start_timer()

    # TODO Get them going - start the retrieve_threads first, then file_reader
    fr.start()
    for t in rts:
        t.start()
    # TODO Wait for them to finish - The order doesn't matter
    fr.join()
    for t in rts:
        t.join()
    log.stop_timer('Time to process all URLS')


if __name__ == '__main__':
    main()