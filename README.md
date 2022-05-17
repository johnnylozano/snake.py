# snake.py
Famous snake game implemented on Raspberry Pi which utilizes physical joystick from the Sense HAT hardware attachment.
## Description:
The player controls a long, thin creature, resembling a snake, which roams around on a bordered plane,
picking up food (or some other item), trying to avoid hitting its own tail or the edges of the playing area.
Each time the snake eats a piece of food, its tail grows longer, making the game increasingly difficult.

## Hardware Requirements:
Intended for Raspberry Pi Model 4 with Sense HAT

## Installation:
- To run this, either run `python3 main.py` or `chmod +x main.py; ./main.py`
- To stop it, press ctrl-c
- To enable/disable on startup, edit sudo nano /etc/rc.local
