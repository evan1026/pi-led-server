import abc
from enum import Enum
from typing import Tuple, Optional, Dict, Type
from .processes import *

from rpi_ws281x import PixelStrip

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


commands: Dict[str, Type[Process]] = {
    'set_brightness': SetBrightnessProcess,
    'set_color': SetColorProcess,
    'halloween1': Halloween1Process,
    'halloween2': Halloween2Process,
    'halloween3': Halloween3Process
}

no_args_commands = ['halloween1', 'halloween2', 'halloween3']


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


def process_command(pipe, wait=False) -> Optional[Process]:
    if wait:
        command = receive_from_pipe(pipe)
    else:
        command = receive_from_pipe(pipe, timeout=0)

    if command is None:
        return None

    try:
        name = command[0]
        args = command[1:]

        process_class = commands[name]
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

    current_process: Process = DoNothingProcess()

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
