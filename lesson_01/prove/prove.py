"""
Course: CSE 251 
Lesson: L01 Prove
File:   prove.py
Author: <Tyler Bartle>

Purpose: Drawing with Python Turtle

The follow program will draw a series of shapes - squares, circles, triangles
and rectangles.  

There is a Python class called cse251Turtle that is used to hold the drawing
commands that are created by the program.  This is required because threads can
not draw to the screen - only the main thread can do this.

Instructions:

- Find the "TODO" comment below and add your code that will use threads.
- You are not allowed to use any other Python modules/packages than the packages
  currently imported below.
- You should create new functions as needed instead of modifying existing functions.
- No global variables.

"""

import math
import threading 
import os
from cse251turtle import *

# Include CSE 251 common Python files. 
from cse251 import *

# No global variables!!!


def draw_square(tur, x, y, side, color='black'):
    """Draw Square"""
    tur.move(x, y)
    tur.setheading(0)
    tur.color(color)
    for _ in range(4):
        tur.forward(side)
        tur.right(90)

def draw_circle(tur, x, y, radius, color='red'):
    """Draw Circle"""
    steps = 10
    circumference = 2 * math.pi * radius

    # Need to adjust starting position so that (x, y) is the center
    x1 = x - (circumference // steps) // 2
    y1 = y
    tur.move(x1 , y1 + radius)

    tur.setheading(0)
    tur.color(color)
    for _ in range(steps):
        tur.forward(circumference / steps)
        tur.right(360 / steps)

def draw_rectangle(tur, x, y, width, height, color='blue'):
    """Draw a rectangle"""
    tur.move(x, y)
    tur.setheading(0)
    tur.color(color)
    tur.forward(width)
    tur.right(90)
    tur.forward(height)
    tur.right(90)
    tur.forward(width)
    tur.right(90)
    tur.forward(height)
    tur.right(90)

def draw_triangle(tur, x, y, side, color='green'):
    """Draw a triangle"""
    tur.move(x, y)
    tur.setheading(0)
    tur.color(color)
    for _ in range(4):
        tur.forward(side)
        tur.left(120)

def draw_coord_system(tur, x, y, size=300, color='black'):
    """Draw corrdinate lines"""
    tur.move(x, y)
    for i in range(4):
        tur.forward(size)
        tur.backward(size)
        tur.left(90)

def draw_squares(tur, lock=None):
    """Draw a group of squares"""
    for x in range(-300, 350, 200):
        for y in range(-300, 350, 200):
            args = [tur, x - 50, y + 50, 100, "black"]
            draw_shape('square', args, lock)

def draw_circles(tur, lock=None):
    """Draw a group of circles"""
    for x in range(-300, 350, 200):
        for y in range(-300, 350, 200):
            args = [tur, x, y-2, 50, "red"]
            draw_shape('circle', args, lock)

def draw_triangles(tur, lock=None):
    """Draw a group of triangles"""
    for x in range(-300, 350, 200):
        for y in range(-300, 350, 200):
            args = [tur, x-30, y-30+10, 60, "blue"]
            draw_shape('triangle', args, lock)

def draw_rectangles(tur, lock=None):
    """Draw a group of Rectangles"""
    for x in range(-300, 350, 200):
        for y in range(-300, 350, 200):
            args = [tur, x-10, y+5, 20, 15, "green"]
            draw_shape('rectangle', args, lock)

def draw_shape(shape, args, lock=None):
    match shape:
        case "square":
            if lock is not None:
                with lock:
                    draw_square(*args)
            else:
                draw_square(*args)
            pass
        case "circle":
            if lock is not None:
                with lock:
                    draw_circle(*args)
            else:
                draw_circle(*args)
            pass
        case "triangle":
            if lock is not None:
                with lock:
                    draw_triangle(*args)
            else:
                draw_triangle(*args)
            pass
        case "rectangle":
            if lock is not None:
                with lock:
                    draw_rectangle(*args)
            else:
                draw_rectangle(*args)
            pass
        case _:
            pass
def run_no_threads(tur, log, main_turtle):
    """Draw different shapes without using threads - DO NOT CHANGE"""

    # !!!!!!!!!!!!!!    DO NOT CHANGE THIS FUNCTION    !!!!!!!!!!!!!!!!!!
    # !!!!!!!!!!!!!!    DO NOT CHANGE THIS FUNCTION    !!!!!!!!!!!!!!!!!!
    # !!!!!!!!!!!!!!    DO NOT CHANGE THIS FUNCTION    !!!!!!!!!!!!!!!!!!
    # !!!!!!!!!!!!!!    DO NOT CHANGE THIS FUNCTION    !!!!!!!!!!!!!!!!!!
    # !!!!!!!!!!!!!!    DO NOT CHANGE THIS FUNCTION    !!!!!!!!!!!!!!!!!!
    # !!!!!!!!!!!!!!    DO NOT CHANGE THIS FUNCTION    !!!!!!!!!!!!!!!!!!

    # Draw Coords system
    tur.pensize(0.5)
    draw_coord_system(tur, 0, 0, size=375)
    tur.pensize(4)

    log.write('-' * 50)
    log.start_timer('\n\nStart Drawing No Threads')
    tur.move(0, 0)

    draw_squares(tur)
    draw_circles(tur)
    draw_triangles(tur)
    draw_rectangles(tur)

    log.step_timer('All drawing commands have been created')

    tur.move(0, 0)
    log.write(f'Number of Drawing Commands: {tur.get_command_count()}')

    # Play the drawing commands that were created
    tur.play_commands(main_turtle)
    log.stop_timer('Total drawing time')
    tur.clear()


def run_with_threads(tur, log, main_turtle):
    """Draw different shapes using threads"""

    # Draw Coord system
    tur.pensize(0.5)
    draw_coord_system(tur, 0, 0, size=375)
    tur.pensize(4)

    log.write('-' * 50)
    log.start_timer('\n\nStart Drawing With Threads')
    tur.move(0, 0)

    # TODO - Start adding your code here.
    # You need to use 4 threads where each thread concurrently drawing one type of shape.
    # You are free to change any functions in this code except those we marked DO NOT CHANGE.
    ##########
    lock = threading.Lock()
    t1 = threading.Thread(target=draw_squares, args=(tur,lock))
    t2 = threading.Thread(target=draw_circles, args=(tur,lock))
    t3 = threading.Thread(target=draw_triangles, args=(tur,lock))
    t4 = threading.Thread(target=draw_rectangles, args=(tur,lock))
    
    t1.start()
    t2.start()
    t3.start()
    t4.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()
    ##########

    log.step_timer('All drawing commands have been created')

    tur.move(0, 0)
    log.write(f'Number of Drawing Commands: {tur.get_command_count()}')

    # Play the drawing commands that were created
    tur.play_commands(main_turtle)
    log.stop_timer('Total drawing time')
    tur.clear()


def main():
    """Main function - DO NOT CHANGE"""

    # !!!!!!!!!!!!!!    DO NOT CHANGE THIS FUNCTION    !!!!!!!!!!!!!!!!!!
    # !!!!!!!!!!!!!!    DO NOT CHANGE THIS FUNCTION    !!!!!!!!!!!!!!!!!!
    # !!!!!!!!!!!!!!    DO NOT CHANGE THIS FUNCTION    !!!!!!!!!!!!!!!!!!
    # !!!!!!!!!!!!!!    DO NOT CHANGE THIS FUNCTION    !!!!!!!!!!!!!!!!!!
    # !!!!!!!!!!!!!!    DO NOT CHANGE THIS FUNCTION    !!!!!!!!!!!!!!!!!!
    # !!!!!!!!!!!!!!    DO NOT CHANGE THIS FUNCTION    !!!!!!!!!!!!!!!!!!

    log = Log(show_terminal=True)

    # create a Screen Object
    screen = turtle.Screen()

    # Screen configuration
    screen.setup(800, 800)

    # Make turtle Object
    main_turtle = turtle.Turtle()
    main_turtle.speed(0)

    # Special CSE 251 Turtle Class
    turtle251 = CSE251Turtle()

    # Test 1 - Drawing with no threads
    # Rename/remove the file "drawpart1.txt" if you want to skip the 
    # drawing of part 1
    if os.path.exists("drawpart1.txt"):
        main_turtle.clear()
        run_no_threads(turtle251, log, main_turtle)
    
    main_turtle.clear()

    # Test 2 - Drawing with threads
    run_with_threads(turtle251, log, main_turtle)

    # Waiting for user to close window
    turtle.done()


if __name__ == "__main__":
    main()
