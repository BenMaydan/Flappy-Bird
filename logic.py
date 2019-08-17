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
import random


def nothing():
    pass


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


class ScoreEngine:
    """
    A blueprint class for detecting if the bird is in between the pipes, granting one score

    Possibly use map / filter / reduce for checking if bird is in the pipe
    """

    def __init__(self, increment=1):
        assert increment > 0, "The score needs to increment by more than 0 every time the bird goes through a pipe!"
        self._score = 0
        self.increment = increment

    def score(self):
        return self._score

    def increase_score(self):
        """
        Increments self.score by self.increment
        :return: self.score
        """
        self._score += self.increment
        return self.score()


class CollisionEngine:
    """
    A blueprint for checking collision between the bird and the pipes currently on the screen

    Possibly use map / filter / reduce for checking collision
    Or write these methods in cython to increase speed slightly
    """

    @staticmethod
    def border_collision(score_engine, bird):
        """
        Checks for collision between the bird and the border
        :return: True or False
        """
        half = (int(curses.LINES / 2) * "\n")
        assert isinstance(bird, Bird), "Bird needs to be an instance of the bird class to access it's title and name!"
        for coordinate in bird.coordinates:
            # Touching the top of the screen
            if coordinate[0] == 0:
                print(half + "{} {} touched the top of the screen!\nYour score was {}".format(
                    bird.title, bird.name,
                    score_engine.score()) + half)
                sys.exit()
            # Touching the bottom of the screen
            if coordinate[0] == curses.LINES:
                print(half + "GAME OVER!\n{} {} touched the bottom of the screen!\nYour score was {}".format(
                    bird.title,
                    bird.name,
                    score_engine.score()) + half)
                sys.exit()

    @staticmethod
    def pipe_collision(score_engine, bird, pipes):
        """
        Checks for collision between the bird and a pipe
        :return: None
        """
        half = (int(curses.LINES / 2) * "\n")
        assert isinstance(bird, Bird)
        for pipe in pipes:
            for coordinate in bird.coordinates:
                if coordinate in pipe.coordinates:
                    print(half + "{} {} touched a pipe!\nYour score was: {}".format(bird.title,
                                                                                    bird.name,
                                                                                    score_engine.score()) + half)
                    sys.exit()

    @staticmethod
    def between_pipe(score_engine, bird, pipes):
        """
        Checks if the bird is between a pipe
        :param score_engine: An instance of the ScoreEngine class
        :param bird: An instance of the Bird class
        :param pipes: A list of all of the pipes on the screen
        :return: True or False
        """
        for pipe in pipes:
            top_left = bird.coordinates[0]
            bottom_right = bird.coordinates[-1]
            # If the top left coordinate of the bird is in the opening of the pipe
            if (pipe.top > top_left[0] > pipe.bottom) and (
                    pipe.coordinates[0][1] < top_left[1] < pipe.coordinates[-1][1]):
                score_engine.increase_score()
                return True
            # If the bottom right coordinate of the bird is in the opening of the pipe
            elif (pipe.top > bottom_right[0] > pipe.bottom) and (
                    pipe.coordinates[0][1] < bottom_right[1] < pipe.coordinates[-1][1]):
                score_engine.increase_score()
                return True
        return False


class Bird:
    """
    Handles flapping and gravity
    """

    def __init__(self, title='Mr.', name='Glappy Glird', char='#'):
        self.char = char
        # Size + coordinates
        self.height = None
        self.width = None
        self.x = None
        self.y = None
        self.coordinates = []

        # Used for printing when the game ends
        self.title = title
        self.name = name

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
                self.coordinates.append((y_coord, x_coord))
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
        self.coordinates = list(map(lambda coordinate: (coordinate[0] - amount, coordinate[1]), self.coordinates))
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

    def coast(self):
        """
        Does not fall and does not flap. AKA does nothing
        :return: None
        """
        pass


class Pipe:
    """
    A blueprint for creating pipes randomly
    """

    def __init__(self, char='&', yrange=None):
        self.char = char

        # Boilerplate code for a method call later to build self
        if yrange is None:
            self.yrange = (0, curses.LINES)
        else:
            self.yrange = yrange
        self.xrange = None
        self.top = None
        self.bottom = None
        self.coordinates = []

    def build(self, width, top, bottom, assertion=True):
        """
        Creates coordinates for the pipe
        :param width: The range of x values for the left side of the pipe to the right side of the pipe
        :param top: The y value for the top of the opening of the pipe
        :param bottom: The y value for the bottom of the opening of the pipe
        :param assertion: Whether or not this method should assert the values given to it are correct. Unsafe to choose False
        :return: Coordinates to draw the pipe
        """
        if assertion:
            # Sanity check for the parameters
            left = width[0]  # Readability
            right = width[1]  # Readability
            assert (left > -1), "The minimum x coordinate of the screen is 0 and you gave {}".format(left)
            assert (right <= curses.COLS - 1), "The maximum x coordinate of the screen is {} and you gave {}".format(
                curses.COLS - 1, right)
            assert (top >= 0), "The minimum y coordinate of the screen is 0 and you gave {} for the top of the " \
                               "opening of the pipe".format(top)
            assert (bottom <= curses.LINES), "The maximum y coordinate of the screen is {} and you gave {} for the " \
                                             "bottom of the opening of the pipe".format(curses.LINES, bottom)
            assert (top < bottom), "Overlapping ends of the opening of the pipe. Top: {}, Bottom: {}\nRemember, " \
                                   "the x axis in curses starts at the top of the screen and the y coordinate " \
                                   "increments " \
                                   "by 1 as it goes down".format(top, bottom)
        self.top = top
        self.bottom = bottom
        self.xrange = width

        self.coordinates = [(y, x) for y in range(self.yrange[0], self.yrange[1]) for x in
                            range(self.xrange[0], self.xrange[1]) if y < top or y >= bottom]
        return self.coordinates

    def delete(self, *x):
        """
        Deletes a column of characters from self.coordinates
        :param x: A range of x coordinates of the columns of the pipe to delete
        :return: The new self.coordinates
        """
        # If the range of x values is empty
        if len(x) == 0:
            return

        # Else delete columns of the pipe like normal
        assert x[0] == 0, "The first number in the range of x coordinates of columns to delete from the pipe needs" \
                          " to be 0 "
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
        # Deletes the pipe on the screen before redrawing. If parts of the pipe are off the screen, it is ignored
        game.long_add(" ", self.coordinates, exception=lambda: nothing())

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
        self.gen_pipe_tick = 0
        self.sleep = sleep

        # This score will be printed at the end. It is incremented every time the snake eats a piece of food
        self.ScoreEngine = ScoreEngine(increment=1)
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
        for pipe in self.pipes[:]:
            # Move the pipe backwards
            pipe.move(self, 3)

            # Draw the new pipe. If there is a curses error, ignore it
            self.long_add(pipe.char, pipe.coordinates, exception=lambda: [nothing()])

            # If the pipe is completely off of the screen, delete the pipe
            if pipe.coordinates[-1][1] < 0:
                self.pipes.remove(pipe)
                del pipe
                continue
        self.refresh()

        # Acts off of user input
        inp = self.getch()
        if inp == 119 or inp == curses.KEY_UP:  # 119 = W key
            self.bird.flap(self, 3)
            # Reset tick value to 0 so bird does not coast fall coast fall etc...
            self.tick_value = 0
        else:
            # Wait one tick before falling
            if self.tick_value == 0:
                self.bird.coast()
                # Don't want the bird to coast forever
                self.tick_value += 1
            else:
                self.bird.fall(self, 2)
                self.tick_value += 1

        # Checks if it is time to generate a pipe
        if self.gen_pipe_tick >= 10:
            new_pipe = Pipe('&')
            random_top = random.randint((curses.LINES // 4) - 10, (curses.LINES // 4) + 10)
            random_bottom = random.randint(((curses.LINES // 4) * 3) - 10, ((curses.LINES // 4) * 3) + 10)
            new_pipe.build(width=(self.pipes[-1].xrange[0] + 10, self.pipes[-1].xrange[1] + 10), top=random_top,
                           bottom=random_bottom, assertion=False)
            self.add_pipe(new_pipe)
            self.long_add(new_pipe.char, new_pipe.coordinates, exception=lambda: [nothing()])
            self.gen_pipe_tick = 0
        else:
            self.gen_pipe_tick += 1

        # Checks for collision before updating the coordinates of the bird on the screen
        CollisionEngine.border_collision(self.ScoreEngine, self.bird)
        CollisionEngine.pipe_collision(self.ScoreEngine, self.bird, self.pipes)
        CollisionEngine.between_pipe(self.ScoreEngine, self.bird, self.pipes)

        # If the game did not end because of a collision, the bird's position is updated
        self.long_add(self.bird.char, self.bird.coordinates)
        self.refresh()
        time.sleep(self.sleep)

        self.gen_pipe_tick += 1

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

    def add(self, char, y, x, exception=lambda: [print("The curses library cannot draw coordinates that are off of "
                                                       "the screen!"), sys.exit()]):
        """
        Draws a single character
        :param char: The character to draw
        :param x: The x coordinate
        :param y: The y coordinate
        :param exception: Performs custom logic when a curses error happens (character is off of the screen)
        :return: None
        """
        add = self.stdscr.addstr
        try:
            add(y, x, char)
        except Exception as e:
            exception()

    def long_add(self, char, coords, exception=lambda: [print("Curses cannot draw coordinates that are off of the "
                                                              "screen!"), sys.exit()]):
        """
        Draws an arbitrary number of characters
        :param char: The unicode character to draw
        :param coords: The coordinates of all of the character
        :param exception: Performs custom logic when a curses error happens (character is off of the screen)
        :return: None
        """
        add = self.add
        for coord in coords:
            add(char, coord[0], coord[1], exception=exception)

    def long_del(self, coords, exception=lambda: [print("Curses cannot draw coordinates that are off of the "
                                                        "screen!"), sys.exit()]):
        """
        Deletes all of the characters at the given coordinates. I.E. Replace with a space
        :param coords: The coordinates of the characters
        :param exception: Performs custom logic when a curses error happens (character is off of the screen)
        :return: None
        """
        add = self.add
        for coord in coords:
            add(' ', coord[0], coord[1], exception=exception)
