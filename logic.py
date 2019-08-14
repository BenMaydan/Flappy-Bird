# The code for generating things
# This will include clouds and the pipes and maybe birds


#
#
# Legal coordinates = (0, 0) -> (curses.LINES - 1, curses.COLS - 1)
# Curses counts coordinates from the top left at(0, 0)
#
#


import curses


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
    def __init__(self, char):
        self.char = char


class Game:
    """
    A class for drawing
    """
    def __init__(self, bird=None, sleep=0.1):
        # Holds the "sprites" currently on the screen
        self.pipes = []
        # If the bird parameter was not given
        assert (isinstance(bird, Bird))
        self.bird = bird

        # This is for the world tick system
        self.tick_value = 0
        assert (sleep >= 0)
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
