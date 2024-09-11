import colorsys
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


# Will write docs later, but the idea of having multiple layers is that depending
# on the direction you want to update in, the pixel you're reading might have already
# been updated, so you go back one layer to get the real previous value
#
# It's dirty and I don't like it but a better solution will take a while and I'd rather do that later if this doesn't work
class MemoryPattern(Pattern, ABC):
    _LAYERS = 2

    def __init__(self):
        self._memory = []
        for i in range(MemoryPattern._LAYERS):
            self._memory.append([])

    def calculate_pixel(self, progress: float, index: int, total_leds: int) -> RGBW:
        self._update_memory_size(total_leds)
        color = self._calculate_pixel_with_memory(progress, index, total_leds)

        for i in range(len(self._memory) - 1):
            self._memory[i + 1][index] = self._memory[i][index]
        self._memory[0][index] = color

        return color

    def color_at(self, index: int, steps_back: int) -> RGBW:
        steps_back = steps_back - 1

        assert steps_back >= 0
        assert index >= 0

        if steps_back >= len(self._memory) or index >= len(self._memory[steps_back]):
            return Color(0, 0, 0)
        return self._memory[steps_back][index]

    @abstractmethod
    def _calculate_pixel_with_memory(self, progress: float, index: int, total_leds: int) -> RGBW:
        pass

    def _update_memory_size(self, total_leds):
        for i in range(len(self._memory)):
            if len(self._memory[i]) < total_leds:
                self._memory[i].extend([Color(0, 0, 0)] * (total_leds - len(self._memory[i])))


# TODO some kind of after update hook for patterns? lots of cases where a pattern wants to know when it's safe to update


def _color_blend(color1: RGBW, color2: RGBW) -> RGBW:
    color1_hsv = colorsys.rgb_to_hsv(color1.r / 255, color1.g / 255, color1.b / 255)
    color2_hsv = colorsys.rgb_to_hsv(color2.r / 255, color2.g / 255, color2.b / 255)

    midpoint = (_avg(color1_hsv[0], color2_hsv[0]),
                _avg(color1_hsv[1], color2_hsv[1]),
                _avg(color1_hsv[2], color2_hsv[2]))

    midpoint_rgb = colorsys.hsv_to_rgb(*midpoint)

    return Color(int(midpoint_rgb[0] * 255), int(midpoint_rgb[1] * 255), int(midpoint_rgb[2] * 255))


def _avg(a: float, b: float) -> float:
    return (a + b) / 2


class ChasePattern(MemoryPattern):

    def __init__(self, sub_pattern: Pattern, blend=False):
        super().__init__()
        self._sub_pattern = sub_pattern
        self._prev_progress = 0
        self._blend = blend

    def _calculate_pixel_with_memory(self, progress: float, index: int, total_leds: int) -> RGBW:
        progress_amount = progress - self._prev_progress
        if progress_amount < 0:
            progress_amount += 1

        leds_to_update = progress_amount * total_leds
        if leds_to_update < 1:
            if index == 0 or not self._blend:
                return self.color_at(index, 1)
            return _color_blend(self.color_at(index, 1), self.color_at(index - 1, 1))

        leds_to_update = int(leds_to_update)

        if index == total_leds - 1:
            self._prev_progress = progress

        if index < leds_to_update:
            return self._sub_pattern.calculate_pixel(progress, index, total_leds)
        else:
            return self.color_at(index - leds_to_update, 2)
