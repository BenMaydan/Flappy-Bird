# A Flappy Bird Clone, Glappy Gird
# Made by Ben Maydan

from logic import Game, Bird, Pipe, CollisionEngine
import curses
import time


bird = Bird(char='#')
collision_engine = CollisionEngine()

with Game(bird=bird, sleep=0.1) as game:
    # The game continues as long as the escape key (ASCII 27) is not pressed
    while game.getch() != 27:
        pipe = Pipe(char="&")
        game.long_add(pipe.char, pipe.build(width=(80, 100), top=50, bottom=40))
