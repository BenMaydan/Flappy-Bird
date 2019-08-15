#
# Legal coordinates = (0, 0) -> (curses.COLS - 1, curses.LINES - 1)
# Curses counts coordinates from the top left at(0, 0)
# Curses coordinates are accessed like this: (y, x)
#

import itertools
import traceback
import time
import curses
import sys


def increasing(values, amount):
    """
    Checks if every value in a list of values increases by some arbitrary amount
    :param values: The list of values
    :param amount: The amount the values in the list should increase by
    :return: True or False
    """
    for current, future in zip(values, values[1:]):
        if current != future - amount:
            return False
    return True


class CollisionEngine:
    """
    A blueprint for checking collision between the bird and the pipes currently on the screen
    """
    @staticmethod
    def border_collision(game):
        """
        Checks for collision between the bird and the border
        :return: True or False
        """
        for coordinate in game.bird.coordinates:
            # Touching the top of the screen
            if coordinate[0] < 0:
                print("GAME OVER!")
                print("Mr. Flappy touched the top of the screen!")
                sys.exit()
            # Touching the bottom of the screen
            if coordinate[0] == curses.LINES:
                print("GAME OVER!")
                print("Mr. Flappy touched the bottom of the screen!")
                sys.exit()

    @staticmethod
    def pipe_collision(game):
        """
        Checks for collision between the bird and a pipe
        :return:
        """


class Bird:
    """
    Handles flapping and gravity
    """
    def __init__(self, char='#'):
        self.char = char
        # Size + coordinates
        self.height = None
        self.width = None
        self.x = None
        self.y = None
        self.coordinates = set()

    def build(self, height=4, width=5, y=30, x=10):
        """
        Returns a set of coordinates to build the bird at (y, x)
        :param height: The height of the bird. The bird is a square
        :param width: The width of the bird. The bird is a square
        :param y: The y coordinate of the center of mass of the bird
        :param x: The x coordinate of the center of mass of the bird
        :return: self.coordinates
        """
        self.height = height
        self.width = width
        self.x = x
        self.y = y
        for y_coord in range(y, y + height):
            for x_coord in range(x, x + width):
                self.coordinates.add((y_coord, x_coord))
        return self.coordinates

    def flap(self, game, amount):
        """
        Flaps the bird
        :param game: An instance of Game
        :param amount: How many pixels the bird should go up when it flaps
        :return: A list of "birds" to draw on the screen to make the bird appear animated
        """
        # Deletes the bird on the screen before redrawing
        game.long_del(self.coordinates)
        # Adjusts every coordinate that makes up the bird to move up some amount
        self.coordinates = list(map(lambda coordinate: (coordinate[0] - amount,  coordinate[1]), self.coordinates))
        return self.coordinates

    def fall(self, game, amount):
        """
        Makes the bird fall with gravity
        :param game: An instance of Game
        :param amount: How many pixels the bird should fall down every tick
        :return: A list of "birds" to draw on the screen to make the bird appear animated
        """
        # Deletes the bird on the screen before redrawing
        game.long_del(self.coordinates)
        # Adjusts every coordinate that makes up the bird to move up some amount
        self.coordinates = list(map(lambda coordinate: (coordinate[0] + amount, coordinate[1]), self.coordinates))
        return self.coordinates


class Pipe:
    """
    A blueprint for creating pipes randomly
    """
    def __init__(self, char='&', yrange=None):
        self.char = char

        # Boilerplate code for a method call later to build self
        self.xrange = None
        self.yrange = (0, curses.LINES)
        self.coordinates = []

    def build(self, width, top, bottom):
        """
        Creates coordinates for the pipe
        :param width: The range of x values for the left side of the pipe to the right side of the pipe
        :param top: The y value for the top of the opening of the pipe
        :param bottom: The y value for the bottom of the opening of the pipe
        :return: Coordinates to draw the pipe
        """
        # Sanity check for the parameters
        left = width[0]  # Readability
        right = width[1]  # Readability
        assert (left > -1), "The minimum x coordinate of the screen is 0 and you gave {}".format(left)
        assert (right <= curses.COLS - 1), "The maximum x coordinate of the screen is {} and you gave {}".format(curses.COLS - 1, right)
        assert (top >= 0), "The minimum y coordinate of the screen is 0 and you gave {} for the top of the opening of " \
                           "the pipe".format(top)
        assert (bottom <= curses.LINES), "The maximum y coordinate of the screen is {} and you gave {} for the bottom " \
                                         "of the opening of the pipe".format(curses.LINES, bottom)
        assert (top < bottom), "Overlapping ends of the opening of the pipe. Top: {}, Bottom: {}\nRemember, " \
                               "the x axis in curses starts at the top of the screen and the y coordinate increments " \
                               "by 1 as it goes down".format(top, bottom)
        self.xrange = width

        for y in range(self.yrange[0], self.yrange[1]):
            for x in range(self.xrange[0], self.xrange[1]):
                # Makes sure it is not adding coordinates to be drawn in the opening of the pipe
                if y < top or y >= bottom:
                    self.coordinates.append((y, x))
                # Don't continue checking if y < top or y > bottom for all of the x's with that same y
                else:
                    break

        # Returns the newly made coordinates
        return self.coordinates

    def delete(self, *x):
        """
        Deletes a column of characters from self.coordinates
        :param x: A range of x coordinates of the columns of the pipe to delete
        :return: The new self.coordinates
        """
        assert x[0] == 0, "The first number in the range of x coordinates of columns to delete from the pipe needs to " \
                          "be 0 "
        assert increasing(x, 1), "The range of x coordinates of columns to delete from the pipe needs to increase by 1"

        # Converts x to a list so we can change the values
        x = list(x)
        # Changes the range of coordinates to fit the x coordinates of the columns
        x = [x_coord for x_coord in range(self.coordinates[0][1], self.coordinates[0][1] + len(x))]

        # Loops over all of the coordinates and checks if they are in the range of x coordinates given
        self.coordinates = [coordinate for coordinate in self.coordinates if coordinate[1] not in x]
        return self.coordinates

    def move(self, game, amount):
        """
        Moves the pipe backwards some amount
        :param game: An instance of the Game class
        :param amount: The amount to move forward or backwards
        :return: The new coordinates
        """
        # Deletes the pipe on the screen before redrawing
        game.long_del(self.coordinates)
        # Adjusts every coordinate that makes up the bird to move up some amount
        self.coordinates = list(map(lambda coordinate: (coordinate[0], coordinate[1] - amount), self.coordinates))
        return self.coordinates


class Game:
    """
    A class for drawing with python curses
    """
    def __init__(self, bird=Bird(char='#'), sleep=0.1):
        # Holds the "sprites" currently on the screen
        self.pipes = []
        self.bird = bird

        # This is for the world tick system
        assert (type(sleep) in [int, float]), "The value of sleep must be an integer or a float"
        assert (sleep >= 0), "The integer value of sleep must be greater than 0"
        self.tick_value = 0
        self.sleep = sleep

        # This score will be printed at the end. It is incremented every time the snake eats a piece of food
        self.score = 0
        self.frozen = False

    def __enter__(self):
        """
        This starts the curses application
        The curses application "prints" to the terminal
        :return: None
        """
        # Initializes the curses application
        self.stdscr = curses.initscr()

        # This hides the cursor
        curses.curs_set(False)

        # A terminal normally captures key presses and prints the key being pressed     (similar to input function)
        # This disables that
        curses.noecho()

        # This function is being called so that the enter key will not have to press enter after clicking a key
        curses.nocbreak()

        # This function call allows the user to enter keys without the program freezing
        self.stdscr.nodelay(True)

        # So the terminal does not return multibyte escape sequences
        # Instead, curses returns something like curses.KEY_LEFT
        self.stdscr.keypad(True)

        # In the use of a context manager, self must be returned
        # So the as keyword can pass along game to the given variable
        return self

    def __exit__(self, type, value, traceback):
        """
        Terminates the curses application and returns control to the terminal
        :return: None
        """
        curses.flash()
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    def tick(self):
        """
        Performs a tick. If the up arrow is not pressed, the bird starts to fall down
        :return: None
        """
        # Moves all of the pipes backwards before allowing any input
        add = self.stdscr.addstr
        for pipe in self.pipes[:]:
            # If the pipe doesn't have coordinates (off of the screen) the except block is triggered
            try:
                if pipe.coordinates[0][1] < 0:
                    # Delete the first three columns of the pipe
                    pipe.delete(0, 1, 2)
                # Keep moving the pipe
                for coord in pipe.move(self, 3):
                    try:
                        add(coord[0], coord[1], pipe.char)
                    except Exception as e:
                        # If the left of the pipe is starting to go off of the screen
                        pass
            except IndexError:
                # The pipe is off of the screen, deleting it is ok
                self.pipes.remove(pipe)
                # Pipe can be garbage collected
                del pipe
        self.refresh()

        # Takes input from the user
        inp = self.getch()
        # 119 = W key
        # curses.KEY_UP = up arrow
        if inp == 119 or inp == curses.KEY_UP:
            self.bird.flap(self, 3)
            # Checks for collision with the border before updating the coordinates of the bird on the screen
            CollisionEngine.border_collision(self)
        else:
            self.bird.fall(self, 2)
            # Checks for collision with the border before updating the coordinates of the bird on the screen
            CollisionEngine.border_collision(self)

        # If the game did not end because of a collision, the bird's position is updated
        self.long_add(self.bird.char, self.bird.coordinates)
        self.refresh()
        time.sleep(self.sleep)

    def getch(self):
        """
        Will return the current key being pressed
        :return: A dict with 'W', 'A', 'D', and the arrows and either 0 or 1 depending on if the key is being pressed or not
        """
        return self.stdscr.getch()

    def refresh(self):
        """
        Refreshes the screen
        :return: None
        """
        self.stdscr.refresh()

    def add_pipe(self, pipe):
        """
        Adds a pipe to self.pipes
        :param pipe: An instance of the Pipe class
        :return: None
        """
        assert isinstance(pipe, Pipe)
        self.pipes.append(pipe)

    def add(self, char, y, x):
        """
        Draws a single character
        :param char: The character to draw
        :param x: The x coordinate
        :param y: The y coordinate
        :return: None
        """
        try:
            self.stdscr.addstr(y, x, char)
        except Exception as e:
            print("Coordinates given: ({}, {})".format(y, x))
            print(
                "Max coordinates of the screen in terms of (y, x): ({}, {})".format(curses.LINES - 1, curses.COLS - 1))
            sys.exit()

    def long_add(self, char, coords):
        """
        Draws an arbitrary number of characters
        :param char: The unicode character to draw
        :param coords: The coordinates of all of the character
        :return: None
        """
        for coord in coords:
            self.add(char, coord[0], coord[1])
        # map is faster
        # map(lambda coord: self.add(char, coord[0], coord[1]), coords)

    def long_del(self, coords):
        """
        Deletes all of the characters at the given coordinates. I.E. Replace with a space
        :param coords: The coordinates of the characters
        :return: None
        """
        for coord in coords:
            self.add(' ', coord[0], coord[1])
        # map is faster
        # map(lambda coord: self.add(' ', coord[0], coord[1]), coords)
