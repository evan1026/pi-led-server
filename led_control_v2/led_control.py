import math
from multiprocessing import Pipe

from rpi_ws281x import PixelStrip

from .command_handling import process_command
from .config import *
from .pattern import NothingPattern, Pattern


class LedStrip(PixelStrip):
    def __init__(self):
        super().__init__(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)


class PatternContext:
    def __init__(self, strip: LedStrip):
        self.current_pattern = NothingPattern()
        self.current_progress = INITIAL_PROGRESS
        self.progress_increment = INITIAL_PROGRESS_INCREMENT
        self.strip = strip


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
    for i in range(strip.getBrightness(), -1, -FADE_OUT_SPEED):
        strip.setBrightness(i)
        strip.show()
    strip.setBrightness(0)
    strip.show()
