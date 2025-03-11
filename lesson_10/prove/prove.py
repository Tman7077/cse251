"""
Course: CSE 251
Lesson Week: 10
File: assignment.py
Author: <Tyler Bartle>

Purpose: assignment for week 10 - reader writer problem

Instructions:

- Review TODO comments

- writer: a process that will send numbers to the reader.  
  The values sent to the readers will be in consecutive order starting
  at value 1.  Each writer will use all of the sharedList buffer area
  (ie., BUFFER_SIZE memory positions)

- reader: a process that receive numbers sent by the writer.  The reader will
  accept values until indicated by the writer that there are no more values to
  process.  

- Do not use try...except statements

- Display the numbers received by the reader printing them to the console.

- Create WRITERS writer processes

- Create READERS reader processes

- You can NOT use sleep() statements.

- You are able (should) to use lock(s) and semaphores(s).  When using locks, you can't
  use the arguments "block=False" or "timeout".  Your goal is to make your
  program as parallel as you can.  Over use of lock(s), or lock(s) in the wrong
  place will slow down your code.

- You must use ShareableList between the two processes.  This shareable list
  will contain different "sections".  There can only be one shareable list used
  between your processes.
  1) BUFFER_SIZE number of positions for data transfer. This buffer area must
     act like a queue - First In First Out.
  2) current value used by writers for consecutive order of values to send
  3) Any indexes that the processes need to keep track of the data queue
  4) Any other values you need for the assignment

- Not allowed to use Queue(), Pipe(), List(), Barrier() or any other data structure.

- Not allowed to use Value() or Array() or any other shared data type from 
  the multiprocessing package.

- When each reader reads a value from the sharedList, use the following code to display
  the value:
  
                    print(<variable from the buffer>, end=', ', flush=True)

Add any comments for me:

Justification for grade:
- I have completed all of the requirements for the assignment.
- I have tested the code and it works as expected.
- I have included comments to explain my code.
- I have followed the instructions and used the required data structures.
- I have used locks and semaphores to ensure that the code is parallel and does not
  use sleep statements.
"""

import random
from multiprocessing.managers import SharedMemoryManager
import multiprocessing as mp

BUFFER_SIZE = 10
READERS = 2
WRITERS = 2

def writer(shared_list, lock, local_items, empty_sem, full_sem, insert_term, total_items):
    """
    Writer process:
    - Writes its allocated items into the circular buffer.
    - Each write waits for an empty slot, writes the next number (from shared_list[BUFFER_SIZE+2]),
      increments that number, updates the head pointer, and signals that an item is available.
    - If insert_term is True (designated writer), after finishing its writes it busy-waits until the
      count of values read (in shared_list[BUFFER_SIZE+3]) equals total_items, and then injects one
      termination marker (-1) per reader.
    """
    for _ in range(local_items):
        empty_sem.acquire() # Wait for an empty slot
        with lock:
            head = shared_list[BUFFER_SIZE] # current head pointer
            shared_list[head] = shared_list[BUFFER_SIZE+2] # write next number
            shared_list[BUFFER_SIZE+2] += 1 # increment next number to send
            shared_list[BUFFER_SIZE] = (head + 1) % BUFFER_SIZE # update head pointer (circular)
        full_sem.release() # Signal that an item is available

    if insert_term:
        # Busy-wait until all valid items have been read.
        while True:
            with lock:
                if shared_list[BUFFER_SIZE+3] >= total_items:
                    break
        # Now inject one termination marker (-1) per reader.
        for _ in range(READERS):
            empty_sem.acquire() # Wait for an empty slot
            with lock:
                head = shared_list[BUFFER_SIZE] # use head pointer to write marker
                shared_list[head] = -1 # termination marker
                shared_list[BUFFER_SIZE] = (head + 1) % BUFFER_SIZE # update head pointer
            full_sem.release() # Signal that a termination marker is available

def reader(shared_list, lock, empty_sem, full_sem):
    """
    Reader process:
    - Waits for an available item.
    - Reads the value from the buffer at the tail pointer.
    - Updates the tail pointer (circularly) and signals that a slot is free.
    - If the value is -1 (termination marker), it breaks the loop.
    - Otherwise, it prints the value and increments the count of values read.
    """
    while True:
        full_sem.acquire() # Wait for an available item
        with lock:
            tail = shared_list[BUFFER_SIZE+1] # Get current tail pointer
            value = shared_list[tail] # Read value from the buffer
            shared_list[BUFFER_SIZE+1] = (tail + 1) % BUFFER_SIZE # Update tail pointer (circular)
        empty_sem.release() # Signal that a slot is now free

        if value == -1: # Termination marker detected
            break

        with lock:
            print(value, end=', ', flush=True)
            shared_list[BUFFER_SIZE+3] += 1 # Increment count of values read
            
def main():

    # This is the number of values that the writer will send to the reader
    items_to_send = random.randint(1000, 10000)

    smm = SharedMemoryManager()
    smm.start()

    # TODO - Create a ShareableList to be used between the processes
    #      - The buffer should be size 10 PLUS at least three other
    #        values (ie., [0] * (BUFFER_SIZE + 3)).  The extra values
    #        are used for the head and tail for the circular buffer.
    #        The another value is the current number that the writers
    #        need to send over the buffer.  This last value is shared
    #        between the writers.
    #        You can add another value to the sharedable list to keep
    #        track of the number of values received by the readers.
    #        (ie., [0] * (BUFFER_SIZE + 4))

    sl = smm.ShareableList([0] * (BUFFER_SIZE + 4))
    sl[BUFFER_SIZE+2] = 1

    # TODO - Create any lock(s) or semaphore(s) that you feel you need
    empty_sem = mp.Semaphore(BUFFER_SIZE)
    full_sem = mp.Semaphore(0)
    lock = mp.Lock()

    items_per_writer = items_to_send // WRITERS
    extra_items = items_to_send % WRITERS

    # TODO - create reader and writer processes
    writers = []
    for i in range(WRITERS):
        local_items = items_per_writer + (1 if i < extra_items else 0)
        # Only writer 0 will inject termination markers.
        insert_term = (i == 0)
        # Pass the global total_items to the designated writer.
        writers.append(mp.Process(target=writer,
                                  args=(sl, lock, local_items, empty_sem, full_sem, insert_term, items_to_send)))

    readers = [mp.Process(target=reader, args=(sl, lock, empty_sem, full_sem)) for _ in range(READERS)]

    # TODO - Start the processes and wait for them to finish
    for w in writers:
        w.start()
    for r in readers:
        r.start()
    for w in writers:
        w.join()
    for r in readers:
        r.join()

    # TODO - Display the number of numbers/items received by the reader.
    #        Can not use "items_to_send", must be a value collected
    #        by the reader processes.
    # print(f'{<your variable>} values received')
    print(f'\n{items_to_send} values sent')
    print(f'{sl[BUFFER_SIZE + 3]} values received')
    smm.shutdown()


if __name__ == '__main__':
    main()
