"""
Course: CSE 251 
Lesson: L02 Team Activity
File:   team.py
Author: <Add name here>

Purpose: Make threaded API calls with the Playing Card API http://deckofcardsapi.com

Instructions:

- Review instructions in Canvas.
"""

from datetime import datetime, timedelta
import threading
import requests
import json

# Include cse 251 common Python files
from cse251 import *

# TODO Create a class based on (threading.Thread) that will
# make the API call to request data from the website

class Request_thread(threading.Thread):
    # TODO - Add code to make an API call and return the results
    def __init__(self, url):
        threading.Thread.__init__(self)
        self.url = url
        self.result = None
    # https://realpython.com/python-requests/
    def run(self):
        response = requests.get(self.url)
        self.result = response.json()

class Deck:

    def __init__(self, deck_id):
        self.id = deck_id
        self.url = f'https://deckofcardsapi.com/api/deck/{self.id}/'
        self.remaining = 52
        self.reshuffle()


    def reshuffle(self):
        print('Reshuffling Deck')
        reshuffle_url = f'{self.url}shuffle/'
        t = Request_thread(reshuffle_url)
        t.start()
        t.join()
        self.remaining = t.result['remaining']
        # TODO - add call to reshuffle


    def draw_card(self):
        draw_url = f'{self.url}draw/?count=1'
        t = Request_thread(draw_url)
        t.start()
        t.join()
        if t.result['success'] == True:
            self.remaining = t.result['remaining']
            return f"{t.result['cards'][0]['value'].title()} of {t.result['cards'][0]['suit'].title()}"
        else:
            return 'No cards left in the deck'
        # TODO add call to get a card

    def cards_remaining(self):
        return self.remaining


    def draw_endless(self):
        if self.remaining == 0:
            self.reshuffle()
        return self.draw_card()


if __name__ == '__main__':

    # TODO - run the program team_get_deck_id.py and insert
    #        the deck ID here.  You only need to run the 
    #        team_get_deck_id.py program once. You can have
    #        multiple decks if you need them

    deck_id = 'nd5rvf0bzwbg'

    # Testing Code >>>>>
    deck = Deck(deck_id)
    for i in range(55):
        card = deck.draw_endless()
        print(f'Card {(i + 1):>2}: {card}', flush=True)
    print()
    # <<<<<<<<<<<<<<<<<<
