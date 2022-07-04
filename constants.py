## Initialize tkinter root
BG_COLOR = "#c45508"

## Layout Variables
BTN_W = 10
BTN_H = 3
BTN_PAD = 30
ENTRY_W = 6
LBL_W = 40
LBL_H = 3

## Control Parameters
def_P = .5
def_I = .05
def_D = 0
SAMP_time = 2
RAMP_time = 75
convergence_bound = .1

MAX_DUTY_CYCLE = 7
MIN_DUTY_CYCLE = 2.5
## Laser Parameters
DEFAULT_FREQ = 40
DEFAULT_DC = 5

MAX_TEMP = 2200
MIN_TEMP = 200
MAX_CURRENT = 20
MIN_CURRENT = 4

LASER_IP="169.254.12.13"
LASER_PORT=5000

SHUTTER_ON = "sso 1\n\r".encode()
SHUTTER_OFF = "sso 0\n\r".encode()

LASER_ON = "smd 1\n\r".encode()
LASER_OFF = "smd 0\n\r".encode()

LASER_ENABLE = "sme 1 \n\r".encode()
## Set Paddings
top_el_padding = (90, 8)
bottom_el_padding = (10, 10)
stg_el_padding = (2, 10)
