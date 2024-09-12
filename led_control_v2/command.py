import uuid
from abc import ABC, abstractmethod
from enum import Enum
from multiprocessing import Pipe
from typing import Optional, Dict, Tuple, Callable, List, Any

from rpi_ws281x import RGBW

from .pattern import Pattern, ColorPattern

CommandHandler = Callable[[Any, List[Any]], Optional[Pattern]]
"""
Function that takes (context: Context, args: List[Any]) and returns the Pattern to switch to
"""


class CommandResponse:
    class Status(Enum):
        OK = 1
        FAILED = 2

    def __init__(self, command_id: uuid, status: Status, data: Any = None):
        self.command_id = command_id
        self.status = status
        self.data = data


class Command(ABC):
    def __init__(self):
        self.id = uuid.uuid4()

    @abstractmethod
    def handle(self, context: Any) -> Tuple[CommandResponse, Optional[Pattern]]:
        pass

    def response(self, status: CommandResponse.Status, data: Any = None) -> CommandResponse:
        return CommandResponse(self.id, status, data)

    def ok_response(self, data: Any = None) -> CommandResponse:
        return self.response(CommandResponse.Status.OK, data)

    def empty_ok_response(self) -> Tuple[CommandResponse, Optional[Pattern]]:
        return self.ok_response(), None


class PatternCommand(Command):
    def __init__(self, pattern: str):
        super().__init__()
        self.pattern = pattern

    def handle(self, context: Any) -> Tuple[CommandResponse, Optional[Pattern]]:
        new_pattern = context.pattern_constructors[self.pattern]()
        return self.ok_response(), new_pattern


class SetColorCommand(Command):
    def __init__(self, color: RGBW):
        super().__init__()
        self.color = color

    def handle(self, context: Any) -> Tuple[CommandResponse, Optional[Pattern]]:
        return self.ok_response(), ColorPattern(self.color)


class SetBrightnessCommand(Command):
    def __init__(self, value: int):
        super().__init__()

        assert 0 <= value <= 255
        self.value = value

    def handle(self, context: Any) -> Tuple[CommandResponse, Optional[Pattern]]:
        context.strip.setBrightness(self.value)
        return self.empty_ok_response()


class GetBrightnessCommand(Command):
    def handle(self, context: Any) -> Tuple[CommandResponse, Optional[Pattern]]:
        return self.ok_response(context.strip.getBrightness()), None


class SetIncrementCommand(Command):
    def __init__(self, value: float):
        super().__init__()
        self.value = value

    def handle(self, context: Any) -> Tuple[CommandResponse, Optional[Pattern]]:
        context.progress_increment = self.value
        return self.empty_ok_response()


class GetIncrementCommand(Command):
    def handle(self, context: Any) -> Tuple[CommandResponse, Optional[Pattern]]:
        return self.ok_response(context.progress_increment), None


def process_command(pipe: Pipe, context: Any) -> Optional[Pattern]:
    command_from_pipe = receive_from_pipe(pipe, timeout=0)

    if command_from_pipe is None:
        return None

    try:
        assert isinstance(command_from_pipe, Command)
        response, new_pattern = command_from_pipe.handle(context)
        pipe.send(response)
        return new_pattern

    except Exception as e:
        print(repr(e))
        pipe.send(command_from_pipe.response(CommandResponse.Status.FAILED, e))
        return None


def receive_from_pipe(pipe, timeout=-1) -> Optional[Command]:
    if timeout < 0 or pipe.poll(timeout):
        return pipe.recv()
    return None
