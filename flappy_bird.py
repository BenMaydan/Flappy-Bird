# A Flappy Bird Clone
# Glappy Gird
# Made by Ben Maydan

from logic import Game, Bird, Pipe, CollisionEngine


bird = Bird(char='#')
pipe = Pipe(char="&")
collision_engine = CollisionEngine()

with Game(sleep=0.1) as game:
    # Automatically starts and terminates curses
    pass
