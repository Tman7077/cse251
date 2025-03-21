"""
Course: CSE 251 
Lesson: L09 Prove Part 2
File:   prove_part_2.py
Author: <Tyler Bartle>

Purpose: Part 2 of prove 9, finding the path to the end of a maze using recursion.

Instructions:
- Do not create classes for this assignment, just functions.
- Do not use any other Python modules other than the ones included.
- You MUST use recursive threading to find the end of the maze.
- Each thread MUST have a different color than the previous thread:
    - Use get_color() to get the color for each thread; you will eventually have duplicated colors.
    - Keep using the same color for each branch that a thread is exploring.
    - When you hit an intersection spin off new threads for each option and give them their own colors.

This code is not interested in tracking the path to the end position. Once you have completed this
program however, describe how you could alter the program to display the found path to the exit
position:

What would be your strategy?

If I were to attempt to display the path that got to the solution,
I would probably reuse some of the logic from the first part of the prove.
Then, once that path has been found, I would instruct the main thread to
always follow that path, and then once it reached a fork in the road,
it would spawn new threads to explore the other paths. This way, the main
thread would always be following the correct path, and the other threads
would be exploring the other paths.

Why would it work?

Because the main thread would already know which directions to go,
it could always take the 'correct' path. Spawning the other threads
would be relatively useless, but maintain the relative functionality
of spawning new threads at forks, even though technically we know
they would be useless in the end.

Justification for grade:
The solve_find_end function successfully finds the end of the maze using
recursive threading. It spawns new threads for each possible move at a fork,
while maintaining the thread that reached a fork first. It then continues
to explore the maze until the end is found. The program also correctly
displays the number of drawing commands and the number of threads created.
"""

import math
import threading 
from screen import Screen
from maze import Maze
import sys
import cv2

# Include cse 251 files
from cse251 import *

SCREEN_SIZE = 700
COLOR = (0, 0, 255)
COLORS = (
    (0,0,255),
    (0,255,0),
    (255,0,0),
    (255,255,0),
    (0,255,255),
    (255,0,255),
    (128,0,0),
    (128,128,0),
    (0,128,0),
    (128,0,128),
    (0,128,128),
    (0,0,128),
    (72,61,139),
    (143,143,188),
    (226,138,43),
    (128,114,250)
)
SLOW_SPEED = 100
FAST_SPEED = 0

# Globals
current_color_index = 0
thread_count = 0
stop = False
speed = SLOW_SPEED

def get_color():
    """ Returns a different color when called """
    global current_color_index
    if current_color_index >= len(COLORS):
        current_color_index = 0
    color = COLORS[current_color_index]
    current_color_index += 1
    return color


# TODO: Add any function(s) you need, if any, here.

def solve_find_end(maze):
    """ Finds the end position using threads. Nothing is returned. """
    global thread_count
    visited = set()
    threads = []
    visited_lock = threading.Lock()
    stop_event = threading.Event()
    stop_event.clear()
    thread_count = 0

    def _solve(maze, pos, color):
        global thread_count
        nonlocal visited
        nonlocal visited_lock
        nonlocal threads
        nonlocal stop_event

        # If the end has been found, return
        if stop_event.is_set():
            return

        # If the position has already been visited, return
        with visited_lock:
            if pos in visited:
                return
            visited.add(pos)  # Mark current position as visited

        maze.move(*pos, color)

        if maze.at_end(*pos):
            stop_event.set()
            return

        possible = maze.get_possible_moves(*pos)
        if not possible:
            return

        # If there is more than one move, spawn new threads for the extras
        if len(possible) > 1:
            for move in possible[1:]:
                if stop_event.is_set():
                    return
                t = threading.Thread(target=_solve, args=(maze, move, get_color()))
                thread_count += 1
                threads.append(t)
                t.start()
            _solve(maze, possible[0], color)
            return
        else:
            _solve(maze, possible[0], color)
            return

    start = maze.get_start_pos()
    t1 = threading.Thread(target=_solve, args=(maze, start, get_color()))
    threads.append(t1)
    t1.start()

    prev_len = -1
    while True:
        for t in threads:
            if t.is_alive():
                t.join(timeout=0.01)
        if len(threads) == prev_len and not any(t.is_alive() for t in threads):
            break
        prev_len = len(threads)



def find_end(log, filename, delay):
    """ Do not change this function """

    global thread_count
    global speed

    # create a Screen Object that will contain all of the drawing commands
    screen = Screen(SCREEN_SIZE, SCREEN_SIZE)
    screen.background((255, 255, 0))

    maze = Maze(screen, SCREEN_SIZE, SCREEN_SIZE, filename, delay=delay)

    solve_find_end(maze)

    log.write(f'Number of drawing commands = {screen.get_command_count()}')
    log.write(f'Number of threads created  = {thread_count}')

    done = False
    while not done:
        if screen.play_commands(speed): 
            key = cv2.waitKey(0)
            if key == ord('1'):
                speed = SLOW_SPEED
            elif key == ord('2'):
                speed = FAST_SPEED
            elif key == ord('q'):
                exit()
            elif key != ord('p'):
                done = True
        else:
            done = True


def find_ends(log):
    """ Do not change this function """

    files = (
        ('very-small.bmp', True),
        ('very-small-loops.bmp', True),
        ('small.bmp', True),
        ('small-loops.bmp', True),
        ('small-odd.bmp', True),
        ('small-open.bmp', False),
        ('large.bmp', False),
        ('large-loops.bmp', False),
        ('large-squares.bmp', False),
        ('large-open.bmp', False)
    )

    log.write('*' * 40)
    log.write('Part 2')
    for filename, delay in files:
        filename = f'./mazes/{filename}'
        log.write()
        log.write(f'File: {filename}')
        find_end(log, filename, delay)
    log.write('*' * 40)


def main():
    """ Do not change this function """
    sys.setrecursionlimit(5000)
    log = Log(show_terminal=True)
    find_ends(log)


if __name__ == "__main__":
    main()