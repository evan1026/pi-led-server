from multiprocessing import Pipe
from typing import Optional, Any, Dict, Tuple

from led_control_v2 import CommandResponse
from led_control_v2.pattern import Pattern


def process_command(commands: Dict[str, Any], pipe: Pipe, wait=False) -> Optional[Pattern]:
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
