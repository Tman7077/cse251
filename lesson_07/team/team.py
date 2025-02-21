"""
Course: CSE 251 
Lesson: L07 Team
File:   team.py
Author: <Add name here>

Purpose: Retrieve Star Wars details from a server.

Instructions:

1) Make a copy of your lesson 2 prove assignment. Since you are  working in a team for this
   assignment, you can decide which assignment 2 program that you will use for the team activity.

2) You can continue to use the Request_Thread() class that makes the call to the server.

3) Convert the program to use a process pool that uses apply_async() with callback function(s) to
   retrieve data from the Star Wars website. Each request for data must be a apply_async() call;
   this means 1 url = 1 apply_async call, 94 urls = 94 apply_async calls.
"""
from datetime import datetime, timedelta
import requests
import json
import threading
import multiprocessing as mp

# Include cse 251 common Python files
from cse251 import *

# Const Values
TOP_API_URL = 'http://127.0.0.1:8790'

# Global Variables
call_count = 0

def RetrieveData(url, key=None):
    response = requests.get(url)
    if response.status_code == 200:
        if key is None:
            return response.json()
        else:
            return response.json()[key]

# TODO Add any functions you need here

def main():
    log = Log(show_terminal=True)
    log.start_timer('Starting to retrieve data from the server')

    global call_count # It was already global

    # TODO Retrieve Top API urls
    data = RetrieveData(TOP_API_URL)
    call_count += 1 # These ones aren't processes, because they're never variable, they just happen once.

    # TODO Retrieve Details on film 6
    film6 = RetrieveData(data['films'] + '6')
    call_count += 1 # These ones aren't processes, because they're never variable, they just happen once.

    # TODO Display results
    # All of the data that needs to be yoinked from the server, in list form
    to_retrieve_list = ['title', 'director', 'producer', 'release_date', 'characters', 'planets', 'starships', 'vehicles', 'species']
    # ^ but dictionary form
    to_retrieve = {}
    for key in to_retrieve_list:
        to_retrieve[key] = film6[key]

    for key, value in to_retrieve.items():
        if key in ['characters', 'planets', 'starships', 'vehicles', 'species']:
            to_print = []
            with mp.Pool(mp.cpu_count()) as pool:
                length = len(value)
                log.write(f'{key.title()}: {length}')
                for i in range(length):
                    call_count += 1
                    pool.apply_async(RetrieveData, args=(value[i], 'name'), callback=to_print.append)
                pool.close()
                pool.join()
            log.write(', '.join(sorted(to_print)))
            log.write()
        else:
            log.write(f'{key.title():<12}: {value.title()}')
            if key == 'release_date':
                log.write()
    
    log.stop_timer('Total Time To complete')
    log.write(f'There were {call_count} calls to the server')

if __name__ == "__main__":
    main()