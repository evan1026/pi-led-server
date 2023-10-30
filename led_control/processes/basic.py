from rpi_ws281x import Color, PixelStrip

from .process import Process, InterruptingProcess


class DoNothingProcess(Process):
    def __init__(self):
        super().__init__(True)

    def run(self, strip: PixelStrip) -> Process:
        return self


class SetColorProcess(Process):

    def __init__(self, color: Color):
        super().__init__(False)
        self.color = color

    def run(self, strip: PixelStrip) -> Process:
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, self.color)
        return DoNothingProcess()


class SetBrightnessProcess(InterruptingProcess):
    def __init__(self, value: int):
        super().__init__(False)
        self.value = value

    def run(self, strip: PixelStrip) -> Process:
        strip.setBrightness(self.value)
        return self.prev_process
