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


# TODO Add any functions you need here


def main():
    log = Log(show_terminal=True)
    log.start_timer('Starting to retrieve data from the server')

    # TODO Retrieve Top API urls
    response = requests.get(TOP_API_URL)
    
    # Check the status code to see if the request succeeded.
    if response.status_code == 200:
        data = response.json()

    # TODO Retrieve Details on film 6
    film6 = requests.get(data['films'] + '6').json()

    # TODO Display results
    to_retrieve = {
        'title': film6['title'],
        'director': film6['director'],
        'producer': film6['producer'],
        'release_date': film6['release_date'],
        'people': film6['characters'],
        'starships': film6['starships'],
        'vehicles': film6['vehicles'],
        'species': film6['species']
    }

    for key, value in to_retrieve.items():
        if key in ['people', 'starships', 'vehicles', 'species']:
            length = len(value)
            print(f'{key.title()}: {length}')
            threads = []
            for i in range(length):
                threads.append(RetrieveData(value[i]))
            to_print = []
            for thread in threads:
                thread.start()
                to_print.append(thread.name)
            for thread in threads:
                thread.join()
            print(*to_print)
        else:
            print(f'{key.title()}: {value.title()}')

    log.stop_timer('Total Time To complete')
    log.write(f'There were {call_count} calls to the server')
    
class RetrieveData(threading.Thread):
    def __init__(self, url):
        threading.Thread.__init__(self)
        self.url = url

    def run(self):
        global call_count
        response = requests.get(self.url)
        call_count += 1
        if response.status_code == 200:
            self.name = response.json()['name'].title()

if __name__ == "__main__":
    main()