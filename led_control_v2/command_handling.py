from enum import Enum
from multiprocessing import Pipe
from typing import Optional, Dict, Tuple, Callable, List, Any

from .pattern import Pattern

CommandHandler = Callable[[Any, List[Any]], Optional[Pattern]]
"""
Function that takes (context: Any, args: List[Any]) and returns the Pattern to switch to
"""


class CommandResponse(Enum):
    OK = 1
    FAILED = 2


def process_command(commands: Dict[str, CommandHandler], pipe: Pipe, wait=False) -> Optional[Pattern]:
    command_from_pipe = receive_from_pipe(pipe, timeout=-1 if wait else 0)

    if command_from_pipe is None:
        return None

    try:
        name, *args = command_from_pipe

        command_handler = commands[name]
        new_pattern = command_handler(args)

        pipe.send(CommandResponse.OK)
        return new_pattern

    except Exception as e:
        print(repr(e))
        pipe.send(CommandResponse.FAILED)
        return None


def receive_from_pipe(pipe, timeout=-1) -> Optional[Tuple[str, ...]]:
    if timeout < 0 or pipe.poll(timeout):
        return pipe.recv()
    return None
