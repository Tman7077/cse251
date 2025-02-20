"""
Course: CSE 251 
Lesson: L06 Prove
File:   prove.py
Author: <Tyler Bartle>

Purpose: Processing Plant

Instructions:

- Implement the necessary classes to allow gifts to be created.

### Justification for grade:
- The program runs without errors and meets all requirements.
- It uses half-duplex (one-way) pipes and closes them as needed.
- It works dynamically with any number of marbles per bag and any number of total marbles.
    - It would even "work" (as in, not break) if total marbles < marbles per bag, but it wouldn't actually send any gifts...
    - It does throw away any partially filled bags if the marble creator is done, but the assignment was unclear on how to handle this, so I just chucked them.
- It uses a shared variable to count the number of gifts created.
"""

import random
import multiprocessing as mp
import os.path
import time
import datetime

# Include cse 251 common Python files - Don't change
from cse251 import *

CONTROL_FILENAME = 'settings.json'
BOXES_FILENAME   = 'boxes.txt'

# Settings constants
MARBLE_COUNT = 'marble-count'
CREATOR_DELAY = 'creator-delay'
NUMBER_OF_MARBLES_IN_A_BAG = 'bag-count'
BAGGER_DELAY = 'bagger-delay'
ASSEMBLER_DELAY = 'assembler-delay'
WRAPPER_DELAY = 'wrapper-delay'

# No Global variables

class Bag():
    """ Bag of marbles - Don't change """

    def __init__(self):
        self.items = []

    def add(self, marble):
        self.items.append(marble)

    def get_size(self):
        return len(self.items)

    def __str__(self):
        return str(self.items)

class Gift():
    """
    Gift of a large marble and a bag of marbles - Don't change

    Parameters:
        large_marble (string): The name of the large marble for this gift.
        marbles (Bag): A completed bag of small marbles for this gift.
    """

    def __init__(self, large_marble, marbles):
        self.large_marble = large_marble
        self.marbles = marbles

    def __str__(self):
        marbles = str(self.marbles)
        marbles = marbles.replace("'", "")
        return f'Large marble: {self.large_marble}, marbles: {marbles[1:-1]}'

class Marble_Creator(mp.Process):
    """ This class "creates" marbles and sends them to the bagger """

    colors = ('Gold', 'Orange Peel', 'Purple Plum', 'Blue', 'Neon Silver', 
        'Tuscan Brown', 'La Salle Green', 'Spanish Orange', 'Pale Goldenrod', 'Orange Soda', 
        'Maximum Purple', 'Neon Pink', 'Light Orchid', 'Russian Violet', 'Sheen Green', 
        'Isabelline', 'Ruby', 'Emerald', 'Middle Red Purple', 'Royal Orange', 
        'Dark Fuchsia', 'Slate Blue', 'Neon Dark Green', 'Sage', 'Pale Taupe', 'Silver Pink', 
        'Stop Red', 'Eerie Black', 'Indigo', 'Ivory', 'Granny Smith Apple', 
        'Maximum Blue', 'Pale Cerulean', 'Vegas Gold', 'Mulberry', 'Mango Tango', 
        'Fiery Rose', 'Mode Beige', 'Platinum', 'Lilac Luster', 'Duke Blue', 'Candy Pink', 
        'Maximum Violet', 'Spanish Carmine', 'Antique Brass', 'Pale Plum', 'Dark Moss Green', 
        'Mint Cream', 'Shandy', 'Cotton Candy', 'Beaver', 'Rose Quartz', 'Purple', 
        'Almond', 'Zomp', 'Middle Green Yellow', 'Auburn', 'Chinese Red', 'Cobalt Blue', 
        'Lumber', 'Honeydew', 'Icterine', 'Golden Yellow', 'Silver Chalice', 'Lavender Blue', 
        'Outrageous Orange', 'Spanish Pink', 'Liver Chestnut', 'Mimi Pink', 'Royal Red', 'Arylide Yellow', 
        'Rose Dust', 'Terra Cotta', 'Lemon Lime', 'Bistre Brown', 'Venetian Red', 'Brink Pink', 
        'Russian Green', 'Blue Bell', 'Green', 'Black Coral', 'Thulian Pink', 
        'Safety Yellow', 'White Smoke', 'Pastel Gray', 'Orange Soda', 'Lavender Purple',
        'Brown', 'Gold', 'Blue-Green', 'Antique Bronze', 'Mint Green', 'Royal Blue', 
        'Light Orange', 'Pastel Blue', 'Middle Green')

    def __init__(self, pipe_out, to_create, delay):
        mp.Process.__init__(self)
        # TODO Add any arguments and variables here
        self.pipe_out = pipe_out
        self.to_create = to_create
        self.delay = delay

    def run(self):
        '''
        for each marble:
            send the marble (one at a time) to the bagger
              - A marble is a random name from the colors list above
            sleep the required amount
        Let the bagger know there are no more marbles
        '''
        # For each marble
        for _ in range(self.to_create):
            # Send the marble to the bagger and sleep
            self.pipe_out.send(random.choice(self.colors))
            time.sleep(self.delay)
        # Close the pipe, signaling to Bagger that MC is done
        # self.pipe_out.close()
        


class Bagger(mp.Process):
    """ Receives marbles from the marble creator, then there are enough
        marbles, the bag of marbles are sent to the assembler """
    def __init__(self, pipe_in, pipe_out, bag_size, delay):
        mp.Process.__init__(self)
        # TODO Add any arguments and variables here
        self.pipe_in = pipe_in
        self.pipe_out = pipe_out
        self.bag_size = bag_size
        self.delay = delay

    def run(self):
        '''
        while there are marbles to process
            collect enough marbles for a bag
            send the bag to the assembler
            sleep the required amount
        tell the assembler that there are no more bags
        '''
        while True:
            # Create a new bag for marbles
            bag = Bag()
            # Until the bag is full
            while bag.get_size() < self.bag_size:
                try: # Receive whatever Marble_Creator sent
                    marble = self.pipe_in.recv()
                    bag.add(marble)
                except EOFError: # If the pipe has been closed
                    # print('Bagger reached end of pipe.')
                    break            
            # If the bag isn't full, don't send it
            if bag.get_size() < self.bag_size: ##### This does mean that if the last bag isn't full, it's just thrown away. Is that right?
                if bag.get_size() != 0: # If there are some marbles in the bag, inform the user
                    print(f'Last bag had {bag.get_size()} of {self.bag_size} marbles, and was discarded.')
                break
            # Otherwise, send the full bag to Assembler and sleep
            self.pipe_out.send(bag)
            time.sleep(self.delay)
        # Close the pipes, signaling to Assembler that Bagger is done
        self.pipe_in.close()
        self.pipe_out.close()


class Assembler(mp.Process):
    """ Take the set of marbles and create a gift from them.
        Sends the completed gift to the wrapper """
    marble_names = ('Lucky', 'Spinner', 'Sure Shot', 'Big Joe', 'Winner', '5-Star', 'Hercules', 'Apollo', 'Zeus')

    def __init__(self, pipe_in, pipe_out, delay):
        mp.Process.__init__(self)
        # TODO Add any arguments and variables here
        self.pipe_in = pipe_in
        self.pipe_out = pipe_out
        self.delay = delay

    def run(self):
        '''
        while there are bags to process
            create a gift with a large marble (random from the name list) and the bag of marbles
            send the gift to the wrapper
            sleep the required amount
        tell the wrapper that there are no more gifts
        '''
        while True:
            try:
                # Receive whatever Bagger sent
                bag = self.pipe_in.recv()
                # Create a gift, send it to Wrapper, and sleep
                gift = Gift(random.choice(self.marble_names), bag)
                self.pipe_out.send(gift)
                time.sleep(self.delay)
            except EOFError: # If the pipe has been closed
                # print('Assembler reached end of pipe.')
                break            
        # Close the pipes, signaling to Wrapper that Assembler is done
        self.pipe_in.close()
        self.pipe_out.close()


class Wrapper(mp.Process):
    """ Takes created gifts and "wraps" them by placing them in the boxes file. """
    def __init__(self, pipe_in, delay, total_gifts):
        mp.Process.__init__(self)
        # TODO Add any arguments and variables here
        self.pipe_in = pipe_in
        self.delay = delay
        self.total_gifts = total_gifts
        
    def run(self):
        '''
        open file for writing
        while there are gifts to process
            save gift to the file with the current time
            sleep the required amount
        '''
        with open(BOXES_FILENAME, 'w') as boxes_file:
            while True:
                try: # Receive whatever Assembler sent
                    gift = self.pipe_in.recv()
                    # Increment total gifts created, write the gift to the file, and sleep
                    self.total_gifts.value += 1
                    # print(f'Wrapper writing gift {self.total_gifts.value}')
                    boxes_file.write(f'Created - {datetime.now().time()}: {gift}\n')
                    time.sleep(self.delay)
                except EOFError: # If the pipe has been closed
                    # print('Wrapper reached end of pipe.')
                    break
        # Close the pipe, signaling to main() that Wrapper is done
        self.pipe_in.close()             


def display_final_boxes(filename, log):
    """ Display the final boxes file to the log file -  Don't change """
    if os.path.exists(filename):
        log.write(f'Contents of {filename}')
        with open(filename) as boxes_file:
            for line in boxes_file:
                log.write(line.strip())
    else:
        log.write_error(f'The file {filename} doesn\'t exist.  No boxes were created.')



def main():
    """ Main function """

    log = Log(show_terminal=True)

    log.start_timer()

    # Load settings file
    settings = load_json_file(CONTROL_FILENAME)
    if settings == {}:
        log.write_error(f'Problem reading in settings file: {CONTROL_FILENAME}')
        return

    log.write(f'Marble count     = {settings[MARBLE_COUNT]}')
    log.write(f'Marble delay     = {settings[CREATOR_DELAY]}')
    log.write(f'Marbles in a bag = {settings[NUMBER_OF_MARBLES_IN_A_BAG]}') 
    log.write(f'Bagger delay     = {settings[BAGGER_DELAY]}')
    log.write(f'Assembler delay  = {settings[ASSEMBLER_DELAY]}')
    log.write(f'Wrapper delay    = {settings[WRAPPER_DELAY]}')

    # TODO: create Pipes between creator -> bagger -> assembler -> wrapper
    # These are Pipe(False)s so they are half-duplex, since I only need to send one-way (and only have to close one end)
    to_b, from_mc = mp.Pipe()
    to_a, from_b  = mp.Pipe()
    to_w, from_a  = mp.Pipe()

    # TODO create variable to be used to count the number of gifts
    total_gifts = mp.Value('i', 0)

    # delete final boxes file
    if os.path.exists(BOXES_FILENAME):
        os.remove(BOXES_FILENAME)

    log.write('Create the processes')

    # TODO Create the processes (ie., classes above)
    mc = Marble_Creator(from_mc, settings[MARBLE_COUNT], settings[CREATOR_DELAY])
    b = Bagger(to_b, from_b, settings[NUMBER_OF_MARBLES_IN_A_BAG], settings[BAGGER_DELAY])
    a = Assembler(to_a, from_a, settings[ASSEMBLER_DELAY])
    w = Wrapper(to_w, settings[WRAPPER_DELAY], total_gifts)

    log.write('Starting the processes')
    # TODO add code here
    mc.start()
    b.start()
    a.start()
    w.start()

    # Close all main() instances of the pipes
    from_mc.close()
    to_b.close()
    from_b.close()
    to_a.close()
    from_a.close()
    to_w.close()

    log.write('Waiting for processes to finish')
    # TODO add code here
    mc.join()
    b.join()
    a.join()
    w.join()

    display_final_boxes(BOXES_FILENAME, log)
    
    # TODO Log the number of gifts created.
    log.write(f'Total gifts created: {total_gifts.value}')

    log.stop_timer(f'Total time')




if __name__ == '__main__':
    main()
