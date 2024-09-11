from enum import Enum
from typing import Tuple, Optional, Dict, Type, Any

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


commands: Dict[str, Any] = {
    'set_brightness': None,
    'set_color': None,
    'set_scale_factor': None,
    'halloween1': None,
    'halloween2': None,
    'halloween3': None
}


no_args_commands = ['halloween1', 'halloween2', 'halloween3']
set_value_commands = ['set_brightness', 'set_scale_factor']


def run_control_loop(pipe):
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()
    strip.show()

    try:
        while True:
            response = process_command(pipe, wait=True)
    except KeyboardInterrupt:
        pass
    finally:
        fade_out(strip)


def fade_out(strip: PixelStrip):
    for i in range(strip.getBrightness(), -1, -32):
        strip.setBrightness(i)
        strip.show()
    strip.setBrightness(0)
    strip.show()


def process_command(pipe, wait=False) -> Optional[Any]:
    command = receive_from_pipe(pipe, timeout=-1 if wait else 0)

    if command is None:
        return None

    try:
        name = command[0]
        args = command[1:]

        command_data = commands[name]
        # TODO
        print(f'({name}, {args}): {command_data}')

        pipe.send(CommandResponse.OK)
        return None

    except Exception as e:
        print(repr(e))
        pipe.send(CommandResponse.FAILED)
        return None


def receive_from_pipe(pipe, timeout=-1) -> Optional[Tuple[str, ...]]:
    if timeout < 0 or pipe.poll(timeout):
        return pipe.recv()
    return None
