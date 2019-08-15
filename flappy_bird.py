# A Flappy Bird Clone, Glappy Gird
# Made by Ben Maydan

from logic import Game, Bird, Pipe, CollisionEngine, increasing
import curses
import time


def save_highscore(score):
    """
    Saves a highscore to a file
    :param score: The score gotten by the user
    :return: None
    """


bird = Bird(char='#')


with Game(bird=bird, sleep=0.2) as game:
    # Add a bird
    game.long_add(bird.char, bird.build(height=3, width=5, y=10, x=10))
    game.refresh()

    # Adds the first pipe
    pipe = Pipe(char='?')
    game.add_pipe(pipe)
    game.long_add(pipe.char, pipe.build(width=(curses.COLS // 2, curses.COLS // 2 + 10), top=20, bottom=30))
    game.refresh()

    # The game continues as long as the escape key (ASCII 27) is not pressed
    while game.getch() != 27:
        game.tick()
        # curses.flushinp()
    save_highscore(100)
    time.sleep(3)
