import time

from rpi_ws281x import Color, PixelStrip

from .process import Process


class Halloween1Process(Process):

    def __init__(self):
        super().__init__(False)
        self.orange = Color(255, 60, 0)
        self.purple = Color(130, 0, 255)
        self.size = 8
        self.offset = 0
        self.wait_ms = 10

    def run(self, strip: PixelStrip) -> Process:
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, self.orange if (i + self.offset) % (self.size * 2) < self.size else self.purple)
        time.sleep(self.wait_ms / 1000.0)

        self.offset += 1
        self.offset %= self.size * 2

        return self


class Halloween2Process(Process):

    def __init__(self):
        super().__init__(False)
        self.orange = Color(255, 60, 0)
        self.purple = Color(130, 0, 255)
        self.current_color = self.orange
        self.offset = 0

    def run(self, strip: PixelStrip) -> Process:
        strip.setPixelColor(self.offset, self.current_color)

        self.offset += 1
        self.offset %= strip.numPixels()

        if self.offset == 0:
            if self.current_color == self.orange:
                self.current_color = self.purple
            else:
                self.current_color = self.orange

        return self


class Halloween3Process(Process):

    def __init__(self):
        super().__init__(False)
        orange = Color(255, 60, 0)
        purple = Color(130, 0, 255)
        black = Color(0, 0, 0)
        self.colors = [orange, orange, black, purple, purple, black]
        self.offset = 0
        self.chases = 6

    def run(self, strip: PixelStrip) -> Process:
        chase_size = strip.numPixels() / self.chases

        for i in range(self.chases):
            strip.setPixelColor((self.offset + int(i * chase_size)) % strip.numPixels(), self.colors[i % len(self.colors)])

        self.offset += 1
        self.offset %= strip.numPixels()

        return self
