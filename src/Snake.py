################################################################################################
## Title: Snake.py
## Author: Johnny Lozano
##
## Hardware Requirements:
##  Intended for Raspberry Pi 4 with Sense HAT
##
## Description:
##   The player controls a long, thin creature, resembling a snake,
##   which roams around on a bordered plane, picking up food (or some other item),
##   trying to avoid hitting its own tail or the edges of the playing area.
##   Each time the snake eats a piece of food, its tail grows longer,
##   making the game increasingly difficult.
##
## Installation:
##   To run this, either run `python3 main.py` or `chmod +x main.py; ./main.py`
##   To stop it, press ctrl-c
##   To enable/disable this on startup, edit sudo nano /etc/rc.local
################################################################################################


from sense_hat import SenseHat
from time import sleep
from random import randrange

####################################
## Global variables and constants ##
####################################

sense = SenseHat()
sense.low_light = True

# Make an 8x8 grid later; placeholder for global variable.
grid = None

# Placeholder for global variable.
snake = None

# Set some constants so we don't have to remember later
APPLE = 1
BODY = 2
HEAD = 3

RED = (255, 0, 0)
PURPLE = (127, 0, 127)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Integer -> color dictionary
color_dict = {
    0: (0, 0, 0),  # blank
    APPLE: (255, 0, 0),  # red apple
    BODY: (0, 255, 0),  # green snake
    HEAD: (0, 0, 255),  # blue head
}


#######################
## Class definitions ##
#######################


class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Snake:
    def __init__(self):
        self.segments = [Vec2(randrange(8), randrange(8))]
        self.direction = [1, 0]

    # @property can be placed above methods to let them be accessed
    # without looking like method calls, e.g. `position = snake.head`
    @property
    def head(self):
        return self.segments[0]

    def grow_snake(self):
        """Grows the snake after the player eats the apple."""

        # Clone the tail
        v = Vec2(self.segments[-1].x, self.segments[-1].y)
        self.segments.append(v)

    def move_snake(self):
        """Moves all segments of the snake by 1 block."""

        # First move all body segments up by 1
        for i in range(len(self.segments) - 1, 0, -1):
            self.segments[i].x = self.segments[i - 1].x
            self.segments[i].y = self.segments[i - 1].y

        # Now update the head
        self.segments[0].x += self.direction[0]
        self.segments[0].y += self.direction[1]

        # And wrap around the field
        self.segments[0].x %= 8
        self.segments[0].y %= 8

    def check_for_collision(self):
        """Checks if snake collides with itself."""

        # Skip the head with segments[1:]
        for segment in self.segments[1:]:
            if segment.x == self.head.x and segment.y == self.head.y:
                return True


######################
## Global functions ##
######################


def wipe_screen():
    """
    Cause a left-to-right screen wipe, starting bright and ending dark
    
    8 shades of grey, from white to black
    """

    greys = []
    c = 255

    # Create the 8 step gradient from white to black
    for i in range(8):
        greys.append((c, c, c))
        c = int(c * ((8 - i) / 8))

    # Pad with 8 blacks
    for i in range(8):
        greys.append((0, 0, 0))

    # How many columns past the right end we are
    over = 0

    # We want to fade *all* squares to black, so we need do 16 instead of 8.
    # xr stands for x right, xl stands for x left.
    for xr in range(17):
        if xr >= 8:
            over += 1
        for xl in range(xr):
            # This... just seems to work. I'm not sure why it's 5 instead of 8.
            colIndex = 5 - xl + over
            # We can't set anything beyond x=7, so just skip them
            if xl > 7:
                break
                # continue
            # Set the whole column to the color
            for y in range(8):
                sense.set_pixel(xl, y, greys[colIndex])
        # Wait for a bit, otherwise it's not really an animation.
        sleep(1 / 8)

    # Ready...
    sense.set_pixel(0, 0, 255, 0, 0)
    sleep(1)
    # Get set...
    sense.set_pixel(7, 0, 255, 255, 0)
    sleep(1)
    # And...
    sense.set_pixel(0, 7, 255, 0, 255)
    sleep(1)
    # Go!
    sense.set_pixel(7, 7, 255, 255, 255)
    sleep(0.1)


def draw_state():
    """Draws the whole grid to the screen"""
    for x in range(len(grid)):
        for y in range(len(grid[x])):
            c = color_dict[grid[x][y]]
            sense.set_pixel(x, y, c)


# Pick a random x and y until the space is empty
def create_apple():
    """Places apple in a random unoccupied space."""
    x = randrange(8)
    y = randrange(8)
    while grid[x][y] != 0:
        x = randrange(8)
        y = randrange(8)

    grid[x][y] = APPLE


# Triggered if all squares are body or head
def win_game():
    """
    Plays animation if player wins the game.
    
    Triggered if all squares are snake body or head.
    """
    # Checkerboard pattern to be filled later
    checker = []

    j = 0
    for i in range(64):
        i = i % 8

        # offset every other row
        if i == 0:
            j += 1

        c = PURPLE if (i + j) % 2 == 0 else WHITE
        checker.append(c)

    # Show 10 frames of animation
    for _ in range(10):
        sense.set_pixels(checker)

        # Swap colors
        for i in range(len(checker)):
            checker[i] = PURPLE if checker[i] == WHITE else WHITE
        sleep(1 / 6)


def update_game():
    """Handles dynamic events of the game."""

    # Wait for 1 second at the start, and speed up the higher the score gets
    sleep((65 - len(snake.segments)) / 64)

    # Get input

    # This is a big queue of events, so process all 'pressed' events.
    es = sense.stick.get_events()
    while len(es) > 0:

        # Get the oldest event.
        e = es[0]

        # Throw out 'released' and 'held' events.
        if e.action == "pressed":
            # Remember that the y axis is flipped compared to math from school.
            if e.direction == "up":
                snake.direction = [0, -1]
            if e.direction == "down":
                snake.direction = [0, 1]
            if e.direction == "left":
                snake.direction = [-1, 0]
            if e.direction == "right":
                snake.direction = [1, 0]

        # Remove oldest event from the queue.
        es.pop(0)

    # update_game positions
    snake.move_snake()

    # Check for lose
    die = snake.check_for_collision()

    # Check for eat
    if grid[snake.head.x][snake.head.y] == APPLE:
        snake.grow_snake()
        # Check for win
        foundEmpty = False
        for x in range(8):
            if foundEmpty:
                break
            for y in range(8):
                if grid[x][y] == 0:
                    foundEmpty = True
                    break
        if foundEmpty:
            create_apple()
        else:
            win_game()
            return False

    # update_game graphics

    ## Clear grid
    for x in range(8):
        for y in range(8):
            # Don't get rid of apples; we use these in gameplay logic.
            # Logic and rendering shouldn't be mixed like this, but... I'm lazy
            if grid[x][y] != APPLE:
                grid[x][y] = 0

    ## Refill grid
    for segment in snake.segments:
        grid[segment.x][segment.y] = BODY
    grid[snake.head.x][snake.head.y] = HEAD

    draw_state()

    return not die


def start_game():
    """Initialize the game"""
    wipe_screen()

    # Make an 8x8 grid
    global grid
    grid = [[0] * 8 for _ in range(8)]

    global snake
    snake = Snake()

    create_apple()


def lose_screen():
    """Animation pattern triggered if the player loses."""

    # Checkerboard pattern to be filled later
    checker = []

    j = 0
    for i in range(64):
        i = i % 8

        # offset every other row
        if i == 0:
            j += 1

        c = RED if (i + j) % 2 == 0 else BLACK
        checker.append(c)

    # Show 10 frames of animation
    for _ in range(10):
        sense.set_pixels(checker)

        # Swap colors
        for i in range(len(checker)):
            checker[i] = RED if checker[i] == BLACK else BLACK
        sleep(1 / 6)

    # Show the score on screen
    sense.show_message("Score: " + str(len(snake.segments)), text_colour=(127, 0, 127))
    sleep(0.1)


###############
## Main loop ##
###############

while True:
    start_game()
    while update_game():
        pass
    lose_screen()

