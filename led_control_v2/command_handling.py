from multiprocessing import Pipe
from typing import Optional, Dict, Tuple, Callable, List, Any

import led_control
from .pattern import Pattern


CommandHandler = Callable[[List[Any]], Optional[Pattern]]


def process_command(commands: Dict[str, CommandHandler], pipe: Pipe, wait=False) -> Optional[Pattern]:
    command_from_pipe = receive_from_pipe(pipe, timeout=-1 if wait else 0)

    if command_from_pipe is None:
        return None

    try:
        name, *args = command_from_pipe

        command_handler = commands[name]
        new_pattern = command_handler(args)

        pipe.send(led_control.CommandResponse.OK)
        return new_pattern

    except Exception as e:
        print(repr(e))
        pipe.send(led_control.CommandResponse.FAILED)
        return None


def receive_from_pipe(pipe, timeout=-1) -> Optional[Tuple[str, ...]]:
    if timeout < 0 or pipe.poll(timeout):
        return pipe.recv()
    return None
