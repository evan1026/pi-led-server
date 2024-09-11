from rpi_ws281x import Color, PixelStrip

from .process import Process, InterruptingProcess, ProcessContext


class DoNothingProcess(Process):
    def __init__(self):
        super().__init__(True)

    def run(self, strip: PixelStrip, context: ProcessContext) -> Process:
        return self


class SetColorProcess(Process):

    def __init__(self, color: Color):
        super().__init__(False)
        self.color = color

    def run(self, strip: PixelStrip, context: ProcessContext) -> Process:
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, self.color)
        return self


class SetBrightnessProcess(Process):
    def __init__(self, value: int):
        super().__init__(False)
        self.value = max(0, min(255, value))

    def set_previous_process(self, prev_process: Process):
        self.prev_process = prev_process

    def run(self, strip: PixelStrip, context: ProcessContext) -> Process:
        curr_brightness = strip.getBrightness()
        diff = self.value - curr_brightness
        diff = max(-5, min(5, diff))
        strip.setBrightness(curr_brightness + diff)
        return self.prev_process if curr_brightness + diff == self.value else self


class SetScaleFactorProcess(InterruptingProcess):
    def __init__(self, value: int):
        super().__init__(False)
        self.value = value

    def run(self, strip: PixelStrip, context: ProcessContext) -> Process:
        context.scale_factor = self.value
        return self.prev_process
