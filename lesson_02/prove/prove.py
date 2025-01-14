"""
Course: CSE 251 
Lesson: L02 Prove
File:   prove.py
Author: <Tyler Bartle>

Purpose: Retrieve Star Wars details from a server

Instructions:

- Each API call must only retrieve one piece of information
- You are not allowed to use any other modules/packages except for the ones used
  in this assignment.
- Run the server.py program from a terminal/console program.  Simply type
  "python server.py" and leave it running.
- The only "fixed" or hard coded URL that you can use is TOP_API_URL.  Use this
  URL to retrieve other URLs that you can use to retrieve information from the
  server.
- You need to match the output outlined in the description of the assignment.
  Note that the names are sorted.
- You are required to use a threaded class (inherited from threading.Thread) for
  this assignment.  This object will make the API calls to the server. You can
  define your class within this Python file (ie., no need to have a separate
  file for the class)
- Do not add any global variables except for the ones included in this program.

The call to TOP_API_URL will return the following Dictionary(JSON).  Do NOT have
this dictionary hard coded - use the API call to get this.  Then you can use
this dictionary to make other API calls for data.

{
   "people": "http://127.0.0.1:8790/people/", 
   "planets": "http://127.0.0.1:8790/planets/", 
   "films": "http://127.0.0.1:8790/films/",
   "species": "http://127.0.0.1:8790/species/", 
   "vehicles": "http://127.0.0.1:8790/vehicles/", 
   "starships": "http://127.0.0.1:8790/starships/"
}

Outline of API calls to server

1) Use TOP_API_URL to get the dictionary above
2) Add "6" to the end of the films endpoint to get film 6 details
3) Use as many threads possible to get the names of film 6 data (people, starships, ...)

"""

from datetime import datetime, timedelta
import requests
import json
import threading

# Include cse 251 common Python files
from cse251 import *

# Const Values
TOP_API_URL = 'http://127.0.0.1:8790'

# Global Variables
call_count = 0


# TODO Add your threaded class definition here
class RetrieveData(threading.Thread):
    def __init__(self, url, key=None):
        threading.Thread.__init__(self)
        # Bet you can't guess what these are for
        self.url = url
        self.key = key
        self.return_value = ''

    def run(self):
        # It was already a global, I swear
        global call_count
        response = requests.get(self.url)
        # Keep track of stats so pretty number matches other pretty number
        call_count += 1
        if response.status_code == 200:
            # If no key was provided, prolly lookin' for a string, which has no [key], so don't ask for it, silly
            if self.key is None:
                self.return_value = response.json()
            # Well, I mean, the opposite of what I just said. :). I'm so funny.
            else:
                self.return_value = response.json()[self.key]

# TODO Add any functions you need here
# Functions? What am I, a delegator? Nah bro, I'm a crocodenial.

def main():
    log = Log(show_terminal=True)
    log.start_timer('Starting to retrieve data from the server')

    # TODO Retrieve Top API urls
    t1 = RetrieveData(TOP_API_URL)
    t1.start()
    t1.join()
    data = t1.return_value

    # TODO Retrieve Details on film 6
    t2 = RetrieveData(data['films'] + '6')
    t2.start()
    t2.join()
    film6 = t2.return_value

    # TODO Display results
    # All of the data that needs to be yoinked from the server, in list form
    to_retrieve_list = ['title', 'director', 'producer', 'release_date', 'characters', 'planets', 'starships', 'vehicles', 'species']
    # All of the data that needs to be yoinked from the server, in dictionary form (as to avoid vain repetition, obviously) (as to avoid vain repetition, obviously)
    to_retrieve = {}
    for key in to_retrieve_list:
        to_retrieve[key] = film6[key]

    # Let's get this bread... aka actually do the assignment here, I guess
    for key, value in to_retrieve.items():
        # If the data to be yoinked is a list of URLs, ask again nicely and thEn print it
        if key in ['characters', 'planets', 'starships', 'vehicles', 'species']:
            length = len(value)
            log.write(f'{key.title()}: {length}')
            # I guess we're sewing with a lot of needles now
            threads = []
            for i in range(length):
                threads.append(RetrieveData(value[i], 'name'))
            to_print = []
            # Start your engines
            for thread in threads:
                thread.start()
            # Okay just kidding
            for thread in threads:
                thread.join()
                # Steal all of their money and run away laughing
                to_print.append(thread.return_value.title())
            # Sort through their money and display the winnings for all to see
            log.write(', '.join(sorted(to_print)))
            log.write()
        # If the data to be yoinked is a string (BORING), just get the printing over with already
        else:
            log.write(f'{key.title():<12}: {value.title()}')
            if key == 'release_date':
                log.write()
    
    # L boring stats
    log.stop_timer('Total Time To complete')
    log.write(f'There were {call_count} calls to the server')

    # If you've read all of the comments up until this point, you're a trooper. I'm sorry for the pain you've endured. I'm not funny, I know.
    # Also, I know this is a lot of comments, but I'm not sorry for that. I'm just sorry for the content of the comments. Or am I? Who am I kidding, no I'm not.
    # Also also, I hope your day is a little brighter because of my silly comments. At least you know they're not just AI-generated and I know what I'm doing!
    # Also also also (for realsies the last one), I am happy to be more professional with my comments in a professional workspace, but this ain't that, chief :) I'm gonna be a dork while I can.

if __name__ == "__main__":
    main()