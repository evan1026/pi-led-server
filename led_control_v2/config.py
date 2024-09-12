from typing import Dict, Any, Optional, List

from rpi_ws281x import Color

from .command import CommandHandler
from .pattern import ColorPattern, FullRandomPattern, Pattern, OnePxChase, Timed, Twice, NTimes, Reversed, ChasePattern, \
    SwitchingPattern, Stretch

LED_COUNT = 300
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0


REFRESH_RATE_TARGET_HZ = 60
INITIAL_PROGRESS = 0
INITIAL_PROGRESS_INCREMENT = 1 / REFRESH_RATE_TARGET_HZ
FADE_OUT_SPEED = 10


patterns = ['halloween1', 'Random Chase', 'RGB Chase', 'Random Waves', 'Full Random (Debug)']
pattern_constructors = {
    'halloween1': lambda: OnePxChase(ColorPattern(Color(255, 127, 0))),
    'Random Chase': lambda: Reversed(ChasePattern(FullRandomPattern())),
    'RGB Chase': lambda: Stretch(4,
                                 ChasePattern(
                                     SwitchingPattern(
                                         [
                                             ColorPattern(Color(255, 0, 0)),
                                             ColorPattern(Color(0, 255, 0)),
                                             ColorPattern(Color(0, 0, 255))
                                         ],
                                         [1, 1, 1]),
                                     blend=True)),
    'Full Random (Debug)': lambda: FullRandomPattern(),
    'Random Waves': lambda: ChasePattern(FullRandomPattern(), blend=True)
}
