from typing import Dict, Any, Optional, List

from rpi_ws281x import Color

from .command import CommandHandler
from .pattern import ColorPattern, FullRandomPattern, Pattern, OnePxChase, Timed, Twice, NTimes, Reversed

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


def _handle_set_brightness(context: Any, args: List[Any]) -> Optional[Pattern]:
    context.strip.setBrightness(args[0])
    return None


commands: Dict[str, CommandHandler] = {
    'set_brightness': _handle_set_brightness,
    'set_color': lambda _, _args: ColorPattern(_args[0]),
    'set_scale_factor': lambda _, __: None,
    'halloween1': lambda _, __: Reversed(Timed(10, NTimes(1000, OnePxChase(ColorPattern(Color(255, 127, 0)))))),
    'halloween2': lambda _, __: None,
    'halloween3': lambda _, __: None,
    'full_random': lambda _, __: FullRandomPattern()
}

no_args_commands = ['halloween1', 'halloween2', 'halloween3', 'full_random']
set_value_commands = ['set_brightness', 'set_scale_factor']
