import time
from abc import ABC, abstractmethod
from random import randint

from rpi_ws281x import RGBW, Color


class Pattern(ABC):

    @abstractmethod
    def calculate_pixel(self, progress: float, index: int, total_leds: int) -> RGBW:
        pass


class NothingPattern(Pattern):
    def calculate_pixel(self, progress: float, index: int, total_leds: int):
        return None


class ColorPattern(Pattern):
    def __init__(self, color: RGBW):
        self.color = color

    def calculate_pixel(self, progress: float, index: int, total_leds: int) -> RGBW:
        return self.color


class FullRandomPattern(Pattern):
    def calculate_pixel(self, progress: float, index: int, total_leds: int) -> RGBW:
        def randi(): return randint(0, 255)
        return Color(randi(), randi(), randi())


class Timed(Pattern):
    def __init__(self, duration: float, sub_pattern: Pattern):
        self._start_time = time.time()
        self._duration = duration
        self._sub_pattern = sub_pattern

    def calculate_pixel(self, progress: float, index: int, total_leds: int) -> RGBW:
        progress = ((time.time() - self._start_time) % self._duration) / self._duration
        return self._sub_pattern.calculate_pixel(progress, index, total_leds)


class NTimes(Pattern):
    def __init__(self, count: int, sub_pattern: Pattern, after: Pattern = None):
        if after is None:
            after = NothingPattern()
        self._count = count
        self._sub_pattern = sub_pattern
        self._after = after
        self._prev_progress = 0

    def calculate_pixel(self, progress: float, index: int, total_leds: int) -> RGBW:
        if self._count > 0:
            return self._do_subpattern(progress, index, total_leds)
        else:
            return self._do_after(progress, index, total_leds)

    def _do_subpattern(self, progress: float, index: int, total_leds: int):
        if self._prev_progress > progress:
            self._count -= 1
        self._prev_progress = progress
        return self._sub_pattern.calculate_pixel(progress, index, total_leds)

    def _do_after(self, progress: float, index: int, total_leds: int):
        return self._after.calculate_pixel(progress, index, total_leds)


class Once(NTimes):
    def __init__(self, sub_pattern: Pattern):
        super().__init__(1, sub_pattern)


class Twice(NTimes):
    def __init__(self, sub_pattern: Pattern):
        super().__init__(2, sub_pattern)


class OnePxChase(Pattern):
    def __init__(self, sub_pattern: Pattern, background: Pattern = None):
        if background is None:
            background = ColorPattern(Color(0, 0, 0))

        self._sub_pattern = sub_pattern
        self._background = background

    def calculate_pixel(self, progress: float, index: int, total_leds: int) -> RGBW:
        active_led = round(progress * total_leds)
        if active_led == index:
            return self._sub_pattern.calculate_pixel(progress, index, total_leds)
        else:
            return self._background.calculate_pixel(progress, index, total_leds)


class Reversed(Pattern):
    def __init__(self, sub_pattern: Pattern):
        self._sub_pattern = sub_pattern

    def calculate_pixel(self, progress: float, index: int, total_leds: int) -> RGBW:
        return self._sub_pattern.calculate_pixel(progress, total_leds - 1 - index, total_leds)