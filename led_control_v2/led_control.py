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


class PatternContext:
    def __init__(self, strip: LedStrip):
        self.current_pattern = NothingPattern()
        self.current_progress = 0
        self.progress_increment = 0.01
        self.strip = strip


commands: Dict[str, CommandHandler] = {
    'set_brightness': lambda context, args: None,
    'set_color': lambda context, args: ColorPattern(args[0]),
    'set_scale_factor': lambda context, args: None,
    'halloween1': lambda context, args: None,
    'halloween2': lambda context, args: None,
    'halloween3': lambda context, args: None,
    'full_random': lambda context, args: FullRandomPattern()
}

no_args_commands = ['halloween1', 'halloween2', 'halloween3', 'full_random']
set_value_commands = ['set_brightness', 'set_scale_factor']


def run_control_loop(pipe):
    context = _init_context()

    try:
        _main_loop(pipe, context)
    except KeyboardInterrupt:
        pass
    finally:
        _fade_out(context.strip)


def _init_context() -> PatternContext:
    strip = LedStrip()
    strip.begin()
    strip.show()
    return PatternContext(strip)


def _main_loop(pipe: Pipe, context: PatternContext):
    while True:
        new_pattern = process_command(commands, pipe, wait=False)
        context.current_pattern = new_pattern if new_pattern is not None else context.current_pattern

        _run_pattern(context, context.current_pattern, context.current_progress)
        context.current_progress = _update_progress(context.current_progress, context.progress_increment)


def _run_pattern(context: PatternContext, pattern: Pattern, progress: float):
    strip = context.strip
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
