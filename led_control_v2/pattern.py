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
