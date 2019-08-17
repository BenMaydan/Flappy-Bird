# A Flappy Bird Clone, Glappy Gird
# Made by Ben Maydan
# A curses exception is caused by curses.ERR

from logic import Game, Bird, Pipe, CollisionEngine, increasing
import curses
import time
import sys


def save_highscore(score):
    """
    Saves a highscore to a file
    :param score: The score gotten by the user
    :return: None
    """


bird = Bird(title='Mr.', name='Glappy Glird', char='#')


with Game(bird=bird, sleep=0.2) as game:
    # Add a bird
    game.long_add(bird.char, bird.build(height=3, width=5, y=10, x=10))
    game.refresh()

    # First pipe
    pipe = Pipe(char='&')
    game.add_pipe(pipe)
    game.long_add(pipe.char, pipe.build(width=(curses.COLS // 2, curses.COLS // 2 + 10), top=20, bottom=30))

    # Second pipe
    pipe2 = Pipe(char='&')
    game.add_pipe(pipe2)
    game.long_add(pipe.char, pipe2.build(width=(130, 140), top=45, bottom=55))

    game.refresh()

    # The game continues as long as the escape key (ASCII 27) is not pressed
    while game.getch() != 27:
        game.tick()
        # curses.flushinp()
    save_highscore(100)
    time.sleep(3)
