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
        strip.show()
        return True


class HalloweenProcess:

    def __init__(self):
        self.orange = Color(255, 60, 0)
        self.purple = Color(130, 0, 255)
        self.size = 8
        self.offset = 0
        self.wait_ms = 50
        self.can_wait = False

    def run(self, strip: PixelStrip) -> bool:
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, self.orange if (i + self.offset) % (self.size * 2) < self.size else self.purple)
        strip.show()
        time.sleep(self.wait_ms / 1000.0)

        self.offset += 1
        self.offset %= self.size * 2

        return False


class DoNothingProcess:
    def __init__(self):
        self.can_wait = True

    def run(self, strip: PixelStrip) -> bool:
        return False


command_names = {
    'set_color': SetColorProcess,
    'halloween': HalloweenProcess
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
    except Exception:
        pipe.send(CommandResponse.FAILED)
        return None


def run_control_loop(pipe):
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()
    strip.show()

    current_process = DoNothingProcess()

    try:
        while True:
            print(f"Stepping {current_process}")
            done = current_process.run(strip)
            if done:
                current_process = DoNothingProcess()

            new_process = process_command(pipe, wait=current_process.can_wait)

            if new_process is not None:
                current_process = new_process

    except KeyboardInterrupt:
        pass
    finally:
        fade_out(strip)
