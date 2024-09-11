from multiprocessing import Process, Pipe, Lock
from typing import Any, List, Iterable

from flask import Flask, request
from flask_api import status
from rpi_ws281x import Color
from werkzeug.datastructures import MultiDict

import led_control_v2 as led_control

app = Flask(__name__)
pipe = None
pipe_mutex = Lock()


class MissingValuesException(Exception):
    def __init__(self, missing_args: List[str]):
        self.missing_args = missing_args


def pipe_send(data: Any) -> Any:
    with pipe_mutex:
        pipe.send(data)
        resp = pipe.recv()
    print(f'{data}: {resp}')
    return resp


def require_args(required_args: Iterable[str], args: MultiDict) -> List[str]:
    values = []
    missing_args = []

    for arg in required_args:
        value = args.get(arg)
        if value is None:
            missing_args.append(arg)
        else:
            values.append(value)

    if len(missing_args) > 0:
        raise MissingValuesException(missing_args)

    return values


def get_return_for_response(response: led_control.CommandResponse):
    if response == led_control.CommandResponse.OK:
        return '', status.HTTP_200_OK
    else:
        return '', status.HTTP_500_INTERNAL_SERVER_ERROR


@app.route('/color', methods=['GET'])
def set_color():
    red, green, blue = require_args(('r', 'g', 'b'), request.args)

    red = int(red)
    green = int(green)
    blue = int(blue)

    resp = pipe_send(('set_color', Color(red, green, blue)))
    return get_return_for_response(resp)


@app.route('/set_value/<path:key>', methods=['GET'])
def set_value(key: str):
    key = 'set_' + key
    if key not in led_control.set_value_commands:
        return "Unknown item", status.HTTP_404_NOT_FOUND

    value, = require_args(('value',), request.args)
    value = int(value)

    resp = pipe_send((key, value))
    return get_return_for_response(resp)


@app.route('/pattern/<path:pattern>', methods=['GET'])
def pattern_input(pattern: str):
    if pattern not in led_control.no_args_commands:
        return "Unknown pattern", status.HTTP_404_NOT_FOUND

    resp = pipe_send((pattern,))

    return get_return_for_response(resp)


@app.route('/', methods=['GET'])
def root():
    return app.send_static_file('index.html')


@app.errorhandler(MissingValuesException)
def handle_missing_params(e: MissingValuesException):
    return "Missing required args: " + str(e.missing_args), status.HTTP_400_BAD_REQUEST

@app.after_request
def add_header(r):
    """
    Add headers to disable caching
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


if __name__ == '__main__':
    parent_conn, child_conn = Pipe()
    p = Process(target=led_control.run_control_loop, args=(child_conn,))

    pipe = parent_conn

    p.start()
    app.run(host="0.0.0.0")
