import math
from typing import Dict

from rpi_ws281x import PixelStrip

from .command_handling import CommandHandler
from .pattern import NothingPattern, ColorPattern, FullRandomPattern

LED_COUNT = 900
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0


class LedStrip(PixelStrip):
    def __init__(self):
        super().__init__(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)


commands: Dict[str, CommandHandler] = {
    'set_brightness': lambda args: None,
    'set_color': lambda args: ColorPattern(args[0]),
    'set_scale_factor': lambda args: None,
    'halloween1': lambda args: None,
    'halloween2': lambda args: None,
    'halloween3': lambda args: None,
    'full_random': lambda args: FullRandomPattern()
}

no_args_commands = ['halloween1', 'halloween2', 'halloween3', 'full_random']
set_value_commands = ['set_brightness', 'set_scale_factor']


def run_control_loop(pipe):
    # import needs to be later to avoid circular reference
    from led_control_v2.command_handling import process_command

    strip = LedStrip()
    strip.begin()
    strip.show()

    current_pattern = NothingPattern()
    current_progress = 0
    progress_increment = 0.01
    try:
        while True:
            new_pattern = process_command(commands, pipe, wait=False)
            current_pattern = new_pattern if new_pattern is not None else current_pattern

            current_pattern.run(strip, current_progress)
            strip.show()

            current_progress += progress_increment
            current_progress = current_progress - math.trunc(current_progress)
    except KeyboardInterrupt:
        pass
    finally:
        fade_out(strip)


def fade_out(strip: PixelStrip):
    for i in range(strip.getBrightness(), -1, -32):
        strip.setBrightness(i)
        strip.show()
    strip.setBrightness(0)
    strip.show()
