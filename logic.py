#
# Legal coordinates = (0, 0) -> (curses.COLS - 1, curses.LINES - 1)
# Curses counts coordinates from the top left at(0, 0)
# Curses coordinates are accessed like this: (y, x)
#


import curses
import sys


class CollisionEngine:
    """
    A blueprint for checking collision between the bird and the pipes currently on the screen
    """
    def __init__(self):
        pass


class Bird:
    """
    Handles flapping and gravity
    """
    def __init__(self, char):
        self.char = char

    def build(self, y, x):
        """
        Returns a set of coordinates to build the bird at (y, x)
        :param y: The y coordinate of the center of mass of the bird
        :param x: The x coordinate of the center of mass of the bird
        :return: Coordinates
        """

    def flap(self, energy):
        """
        Flaps the bird
        :param energy: How much the bird should go up when it flaps
        :return: A list of "birds" to draw on the screen to make the bird appear animated
        """

    def fall(self, amount):
        """
        Makes the bird fall with gravity
        :param amount: How much the bird should fall down every "individual" fall
        :return: A list of "birds" to draw on the screen to make the bird appear animated
        """


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
        assert (left > 0), "The minimum x coordinate of the screen is 0 and you gave {}".format(left)
        assert (right < curses.COLS), "The maximum x coordinate of the screen is {} and you gave {}".format(curses.COLS - 1, right)
        assert (top > 0), "The minimum y coordinate of the screen is 0 and you gave {} for the top of the opening of the pipe".format(top)
        assert (bottom < curses.LINES - 1), "The maximum y coordinate of the screen is {} and you gave {} for the bottom of the opening of the pipe".format(curses.LINES, bottom)
        assert (top > bottom), "Overlapping ends of the opening of the pipe. Top: {}, Bottom: {}".format(top, bottom)
        self.xrange = width

        for x in range(self.xrange[0], self.xrange[1]):
            for y in range(self.yrange[0], self.yrange[1]):
                # Makes sure it is not adding coordinates to be drawn in the opening of the pipe
                if y < top or y > bottom:
                    print("y, x:", y, x)
                    self.coordinates.append((y, x))
                # # Don't continue checking if y < top or y > bottom for all of the x's with that same y
                # else:
                #     break

        # Returns the newly made coordinates
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

        # This function is being called so that the enter key will not have to be pressed after clicking a key
        curses.cbreak()

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

    def getch(self):
        """
        Will return the current key being pressed
        :return: A dict with 'W', 'A', 'D', and the arrows and either 0 or 1 depending on if the key is being pressed or not
        """
        return self.stdscr.getch()

    def add(self, char, y, x):
        """
        Draws a single character
        :param char: The character to draw
        :param x: The x coordinate
        :param y: The y coordinate
        :return: None
        """
        self.stdscr.addstr(y, x, char)

    def long_add(self, char, coords):
        """
        Draws an arbitrary number of characters
        :param char: The unicode character to draw
        :param coords: The coordinates of all of the character
        :return: None
        """
        for coord in coords:
            try:
                self.stdscr.addstr(coord[0], coord[1], char)
            except Exception as e:
                print("Curses self.stdscr.addstr encountered an ERR")
                print("Coordinates given: ({}, {})".format(coord[0], coord[1]))
                print("Max coordinates of the screen in terms of (y, x): ({}, {})".format(curses.LINES, curses.COLS))
                sys.exit()
