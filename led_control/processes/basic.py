from rpi_ws281x import Color, PixelStrip

from .process import Process


class SetColorProcess(Process):

    def __init__(self, color: Color):
        super().__init__(False)
        self.color = color

    def run(self, strip: PixelStrip) -> bool:
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, self.color)
        return True


class DoNothingProcess(Process):
    def __init__(self):
        super().__init__(True)

    def run(self, strip: PixelStrip) -> bool:
        return False


class SetBrightnessProcess(Process):
    def __init__(self, value: int):
        super().__init__(False)
        self.value = value

    def run(self, strip: PixelStrip) -> bool:
        strip.setBrightness(self.value)
        return True
