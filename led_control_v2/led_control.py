import math
import time
from multiprocessing import Pipe

from rpi_ws281x import PixelStrip

from .command_handling import process_command
from .config import *
from .pattern import Pattern, NothingPattern


class LedStrip(PixelStrip):
    def __init__(self):
        super().__init__(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)


class Context:
    def __init__(self, strip: PixelStrip):
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


def _init_context() -> Context:
    strip = LedStrip()
    strip.begin()
    strip.show()
    return Context(strip)


def _main_loop(pipe: Pipe, context: Context):
    while True:
        start_time = time.time()

        new_pattern = process_command(commands, pipe, context, wait=False)
        if new_pattern is not None:
            context.current_pattern = new_pattern
            context.current_progress = INITIAL_PROGRESS

        _run_pattern(context, context.current_pattern, context.current_progress)
        context.current_progress = _update_progress(context.current_progress, context.progress_increment)

        duration = time.time() - start_time
        target_duration = 1 / REFRESH_RATE_TARGET_HZ
        sleep_time = target_duration - duration

        if sleep_time > 0:
            time.sleep(sleep_time)


def _run_pattern(context: Context, pattern: Pattern, progress: float):
    strip = context.strip
    for i in range(strip.numPixels()):
        color = pattern.calculate_pixel(progress, i, strip.numPixels())
        if color is not None:
            strip.setPixelColor(i, color)
    strip.show()


def _update_progress(progress: float, progress_increment: float) -> float:
    progress += progress_increment
    return progress - math.trunc(progress)


def _fade_out(strip: PixelStrip):
    for i in range(strip.getBrightness(), -1, -FADE_OUT_SPEED):
        strip.setBrightness(i)
        strip.show()
    strip.setBrightness(0)
    strip.show()
