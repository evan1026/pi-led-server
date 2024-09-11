from enum import Enum
from typing import Dict, Any

from rpi_ws281x import PixelStrip

LED_COUNT = 900
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0


class LedStrip(PixelStrip):
    def __init__(self):
        super().__init__(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)


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
    # import needs to be later to avoid circular reference
    from led_control_v2.command_handling import process_command

    strip = LedStrip()
    strip.begin()
    strip.show()

    current_pattern = None  # TODO suitable default
    try:
        while True:
            new_pattern = process_command(commands, pipe, wait=True)
            current_pattern = new_pattern if new_pattern is not None else current_pattern
            # TODO run current pattern
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
