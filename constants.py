SCALE_FACTOR = 1.25
SCREEN_WIDTH, SCREEN_HEIGHT = int(540 * SCALE_FACTOR), int(660 * SCALE_FACTOR)
GRID_SIZE = int(20 * SCALE_FACTOR)
FPS = 60
PACMAN_SPEED = int(3 * SCALE_FACTOR)
GHOST_SPEED = PACMAN_SPEED * 20
SPRITE_SIZE = int(13 * SCALE_FACTOR)
ANIMATION_SPEED = 0.05
LIVES = 3
MAZE_DIFFICULTY = "medium" # easy/medium/hard

FONT = "fonts/Retro Gaming.ttf"

PACMAN_MOVING_PATH = 'sprites/pacman.png'
PACMAN_DEATH_PATH = 'sprites/pacman_death.png'

GHOST_DEATH_PATH = 'sprites/frightened_1.png'

PINKY = 'sprites/pinky.png'
BLINKY = 'sprites/blinky.png'
CLYDE = 'sprites/clyde.png'
INKY = 'sprites/inky.png'

EAT_DOT_1 = "sounds/eat_dot_1.wav"
EAT_DOT_0 = "sounds/eat_dot_0.wav"
STARTSOUND = "sounds/start.wav"
RESTARTSOUND = "sounds/restart.wav"
DEATHSOUND = "sounds/death_0.wav"

BLACK = (0, 0, 0)
BLUE = (0, 0, 155)
RED = (155, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)