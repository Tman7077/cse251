"""
Authors: Luc Comeau, Hunter Wilhelm, and Christopher Keers
License: MIT
"""

import os
import time
import logging
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import json

def clear_output():
    print("\033c", end="", flush=True)


def set_working_directory(file_path):
    """
    Sets the current working directory to the folder specified
    
    Parameters:
        file_path (str): The path to the folder to use as the working directory.
    """
    os.chdir(os.path.dirname(os.path.realpath(file_path)))


def print_dict(dict, title='', indent=2):
    """
    Display a dictionary in a structured format.

    Parameters:
        dict (dict): The dictionary to pretty print.
        title [str]: A title line to print before the dictionary if desired.
        indent (int): How much to indent each succeeding level of the dictionary; default 2.
    """
    if title != '':
        print(f'Dictionary: {title}')
    print(json.dumps(dict, indent=indent))


def load_json_file(filename):
    """
    Attempts to load and parse a json file.

    Parameters:
        filename (str): The path including filename of the json file to attempt to open.

    Returns:
        dict: The parsed json or an empty dictionary.
    """
    if os.path.exists(filename):
        with open(filename) as json_file: 
            data = json.load(json_file)
        return data
    else:
        return {}


class Log():
    """
    A custom Logger Class for CSE 251.

    Parameters:
        filename_log [str]: What to name the log file; default is [timestamp].log
        linefmt [str]: The Logger format to use for lines logged; default `%(message)s`
        show_levels [bool]: Set to True to record levels when necessary; default False.
        include_time [bool]: Set to False to exclude adding timestamps to lines; default True.
        append_mode [bool]: Set to True to append to previous log; default False, overwrite.
    """
    def __init__(self, filename_log='',
                linefmt='',
                show_levels=False,
                show_terminal=False,
                include_time=True,
                append_mode=False):
        self._start_time = time.perf_counter()
        self._show_terminal = show_terminal

        # Create a `logs` directory if it does not exist already.
        if not os.path.exists('logs'):
   	        os.makedirs('logs')

        # If not name was given for the log file use a timestamp.
        if filename_log == '':
            d = datetime.now()
            localtime = d.strftime("%m%d-%H%M%S")
            filename_log = f'{localtime}.log'

        # Prepend the `logs` directory to the filename.
        self._filename = 'logs/' + filename_log

        # Set our default line format if the user did not provide one.
        if linefmt == '':
            linefmt = '%(message)s'
        
        # Modify `linefmt` if the user would like levels to be shown.
        if show_levels:
            linefmt = '%(levelname)s - ' + linefmt

        # Modify `linefmt` to prepend a timestamp if the user requested it.
        if include_time:
            date_format = '%H:%M:%S'
            linefmt = '%(asctime)s| ' + linefmt
        else:
            date_format = ''

        # Determine the correct log mode: write (overwrite) or append.
        mode = 'w'
        if append_mode:
            mode = 'a'

        # Create and configure logger.
        logging.basicConfig(filename=self._filename,
                            # format='%(asctime)s %(levelname)s %(message)s',
                            format=linefmt,
                            datefmt=date_format,
                            filemode=mode)

        self.logger = logging.getLogger()

        # Setting the threshold of logger to DEBUG.
        self.logger.setLevel(logging.INFO)

        # If the user requested terminal output show the message in the terminal as well.
        if show_terminal:
            formatter = logging.Formatter(linefmt, datefmt=date_format)
            terminal_handler = logging.StreamHandler()
            terminal_handler.setFormatter(formatter)
            self.logger.addHandler(terminal_handler)


    def start_timer(self, message=''):
        """
        Start (restart) the timer.

        NOTE: This is automatically done when the Log class is initialized.

        Parameter:
            message [str]: Optional message to print as you restart the timer.
        """
        if message != '':
            self.write(message)
            
        self._start_time = time.perf_counter()


    def step_timer(self, message=''):
        """
        Get the current timer value.

        Parameter:
            message [str]: Optional message to print as you restart the timer.
        """
        t = time.perf_counter() - self._start_time
        if message == '':
            self.write(f'{t:0.8f}')
        else:
            self.write(f'{message} = {t:0.8f}')
        return t


    def stop_timer(self, message=''):
        """
        Stop the timer, and report the elapsed time.
        
        Parameter:
            message [str]: Optional message to print as you restart the timer.
        """
        t = time.perf_counter() - self._start_time
        if message == '':
            self.write(f'{t:0.8f}')
        else:
            self.write(f'{message} = {t:0.8f}')
        return t


    def get_time(self):
        """ Get your own version of the counter (timer). """
        return time.perf_counter()


    def write_blank_line(self):
        """ Write a blank line to the log file. """
        self.logger.info(' ')


    def write(self, message=''):
        """
        Write info message to log file.
        
        parameters:
            message [str]: What you would like written to the log file.
        """
        self.logger.info(message)


    def write_warning(self, message=''):
        """
        Write warning message to log file.
        
        parameters:
            message [str]: What you would like written to the log file.
        """
        self.logger.warning('WARNING: ' + message)


    def write_error(self, message=''):
        """
        Write error message to log file.
        
        parameters:
            message [str]: What you would like written to the log file.
        """
        self.logger.error('ERROR: ' + message)


class Plots:
    """
    Create plots for reports.

    Parameters:
        title [str]: A title for the plot graph.
    """
    def __init__(self, title=''):
        self._title = title

    def line(self,
            xdata,
            ydata,
            desc='',
            title='',
            x_label='',
            y_label='',
            show_plot=True,
            filename=''):
        """
        Create a line plot.

        Parameters:
            xdata: X-axis data.
            ydata: Y-axis data.
            desc [str]: Description of the plot.
            title [str]: Title of the plot.
            x_label [str]: Label for the X-axis.
            y_label [str]: Label for the Y-axis.
            show_plot [bool]: Whether to display the plot; default True.
            filename [str]: Filename to save the plot.
        """
        plt.plot(xdata, ydata)

        if title == '':
            title = self._title

        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        plt.grid()

        if filename != '':
            plt.savefig(filename)

        if show_plot:
            plt.show()

    def bar(self,
            xdata,
            ydata,
            desc='',
            title='',
            x_label='',
            y_label='',
            show_plot=True,
            filename=''):
        """
        Create a bar plot.

        Parameters:
            xdata: X-axis data.
            ydata: Y-axis data.
            desc [str]: Description of the plot.
            title [str]: Title of the plot.
            x_label [str]: Label for the X-axis.
            y_label [str]: Label for the Y-axis.
            show_plot [bool]: Whether to display the plot; default True.
            filename [str]: Filename to save the plot.
        """
        plt.bar(xdata, ydata)

        if title == '':
            title = self._title

        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        plt.grid()

        if filename != '':
            plt.savefig(filename)

        if show_plot:
            plt.show()