import abc

from rpi_ws281x import PixelStrip


class Process(abc.ABC):
    def __init__(self, can_wait: bool):
        self.can_wait = can_wait

    @abc.abstractmethod
    def run(self, strip: PixelStrip) -> bool:
        pass