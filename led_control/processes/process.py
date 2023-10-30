import abc

from rpi_ws281x import PixelStrip


class ProcessContext:
    def __init__(self, scale_factor):
        self.scale_factor = scale_factor


class Process(abc.ABC):
    def __init__(self, can_wait: bool):
        self.can_wait = can_wait

    @abc.abstractmethod
    def run(self, strip: PixelStrip, context: ProcessContext) -> "Process":
        pass


class InterruptingProcess(Process, abc.ABC):

    def __init__(self, can_wait: bool):
        super().__init__(can_wait)
        self.prev_process = None

    def set_previous_process(self, prev_process: Process):
        self.prev_process = prev_process
