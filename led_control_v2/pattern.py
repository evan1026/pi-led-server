from abc import ABC, abstractmethod
from random import randint

from rpi_ws281x import PixelStrip, RGBW, Color


class Pattern(ABC):
    @abstractmethod
    def run(self, strip: PixelStrip, progress: float):
        pass


class NothingPattern(Pattern):
    def run(self, strip: PixelStrip, progress: float):
        pass


class ColorPattern(Pattern):
    def __init__(self, color: RGBW):
        self.color = color

    def run(self, strip: PixelStrip, progress: float):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, self.color)


class FullRandomPattern(Pattern):
    def run(self, strip: PixelStrip, progress: float):
        for i in range(strip.numPixels()):
            def randi(): return randint(0, 255)
            strip.setPixelColor(i, Color(randi(), randi(), randi()))
