import math
from multiprocessing import Pipe
from typing import Dict

from rpi_ws281x import PixelStrip

from .command_handling import CommandHandler, process_command
from .pattern import NothingPattern, ColorPattern, FullRandomPattern, Pattern

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
    strip = _init_strip()

    try:
        _main_loop(pipe, strip)
    except KeyboardInterrupt:
        pass
    finally:
        _fade_out(strip)


def _init_strip() -> LedStrip:
    strip = LedStrip()
    strip.begin()
    strip.show()
    return strip


def _main_loop(pipe: Pipe, strip: LedStrip):
    current_pattern = NothingPattern()
    current_progress = 0
    progress_increment = 0.01

    while True:
        new_pattern = process_command(commands, pipe, wait=False)
        current_pattern = new_pattern if new_pattern is not None else current_pattern

        _run_pattern(strip, current_pattern, current_progress)
        current_progress = _update_progress(current_progress, progress_increment)


def _run_pattern(strip: LedStrip, pattern: Pattern, progress: float):
    for i in range(strip.numPixels()):
        color = pattern.calculate_pixel(progress, i, strip.numPixels())
        if color is not None:
            strip.setPixelColor(i, color)
    strip.show()


def _update_progress(progress: float, progress_increment: float) -> float:
    progress += progress_increment
    return progress - math.trunc(progress)


def _fade_out(strip: LedStrip):
    for i in range(strip.getBrightness(), -1, -10):
        strip.setBrightness(i)
        strip.show()
    strip.setBrightness(0)
    strip.show()
