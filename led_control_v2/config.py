from typing import Dict

from .command_handling import CommandHandler
from .pattern import ColorPattern, FullRandomPattern

LED_COUNT = 900
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0


INITIAL_PROGRESS = 0
INITIAL_PROGRESS_INCREMENT = 0.01
FADE_OUT_SPEED = 10


commands: Dict[str, CommandHandler] = {
    'set_brightness': lambda _, __: None,
    'set_color': lambda _, _args: ColorPattern(_args[0]),
    'set_scale_factor': lambda _, __: None,
    'halloween1': lambda _, __: None,
    'halloween2': lambda _, __: None,
    'halloween3': lambda _, __: None,
    'full_random': lambda _, __: FullRandomPattern()
}

no_args_commands = ['halloween1', 'halloween2', 'halloween3', 'full_random']
set_value_commands = ['set_brightness', 'set_scale_factor']
