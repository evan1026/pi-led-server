import time
from enum import Enum
from typing import Tuple, Optional, Any

from rpi_ws281x import Color, PixelStrip

LED_COUNT = 900
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0


class CommandResponse(Enum):
    OK = 1
    FAILED = 2


class SetColorProcess:

    def __init__(self, color: Color):
        self.color = color
        self.can_wait = False

    def run(self, strip: PixelStrip) -> bool:
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, self.color)
        return True


class Halloween1Process:

    def __init__(self):
        self.orange = Color(255, 60, 0)
        self.purple = Color(130, 0, 255)
        self.size = 8
        self.offset = 0
        self.wait_ms = 10
        self.can_wait = False

    def run(self, strip: PixelStrip) -> bool:
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, self.orange if (i + self.offset) % (self.size * 2) < self.size else self.purple)
        time.sleep(self.wait_ms / 1000.0)

        self.offset += 1
        self.offset %= self.size * 2

        return False


class Halloween2Process:

    def __init__(self):
        self.orange = Color(255, 60, 0)
        self.purple = Color(130, 0, 255)
        self.current_color = self.orange
        self.offset = 0
        self.can_wait = False

    def run(self, strip: PixelStrip) -> bool:
        strip.setPixelColor(self.offset, self.current_color)

        self.offset += 1
        self.offset %= strip.numPixels()

        if self.offset == 0:
            if self.current_color == self.orange:
                self.current_color = self.purple
            else:
                self.current_color = self.orange

        return False


class Halloween3Process:

    def __init__(self):
        orange = Color(255, 60, 0)
        purple = Color(130, 0, 255)
        black = Color(0, 0, 0)
        self.colors = [orange, orange, black, purple, purple, black]
        self.offset = 0
        self.chases = 6
        self.can_wait = False

    def run(self, strip: PixelStrip) -> bool:
        chase_size = strip.numPixels() / self.chases

        for i in range(self.chases):
            strip.setPixelColor((self.offset + int(i * chase_size)) % strip.numPixels(), self.colors[i % len(self.colors)])

        self.offset += 1
        self.offset %= strip.numPixels()

        return False


class DoNothingProcess:
    def __init__(self):
        self.can_wait = True

    def run(self, strip: PixelStrip) -> bool:
        return False


command_names = {
    'set_color': SetColorProcess,
    'halloween1': Halloween1Process,
    'halloween2': Halloween2Process,
    'halloween3': Halloween3Process
}


def fade_out(strip: PixelStrip):
    for i in range(255, -1, -32):
        strip.setBrightness(i)
        strip.show()
    strip.setBrightness(0)
    strip.show()


def receive_from_pipe(pipe, timeout=-1) -> Optional[Tuple[str, ...]]:
    if timeout < 0 or pipe.poll(timeout):
        return pipe.recv()
    return None


def process_command(pipe, wait=False):
    if wait:
        command = receive_from_pipe(pipe)
    else:
        command = receive_from_pipe(pipe, timeout=0)

    if command is None:
        return None

    try:
        name = command[0]
        args = command[1:]

        process_class = command_names[name]
        process = process_class(*args)

        pipe.send(CommandResponse.OK)
        return process
    except Exception as e:
        print(repr(e))
        pipe.send(CommandResponse.FAILED)
        return None


def run_control_loop(pipe):
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()
    strip.show()

    speed = 6

    current_process = DoNothingProcess()

    try:
        while True:
            for _ in range(speed):
                done = current_process.run(strip)

                if done:
                    current_process = DoNothingProcess()

            strip.show()

            new_process = process_command(pipe, wait=current_process.can_wait)

            if new_process is not None:
                current_process = new_process

    except KeyboardInterrupt:
        pass
    finally:
        fade_out(strip)
