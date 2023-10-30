from multiprocessing import Process, Pipe, Lock
from typing import Any

from flask import Flask, request
from flask_api import status
from rpi_ws281x import Color

import led_control

app = Flask(__name__)
pipe = None
pipe_mutex = Lock()


def pipe_send(data: Any):
    with pipe_mutex:
        pipe.send(data)
        return pipe.recv()


@app.route('/color', methods=['GET'])
def set_color_endpoint():
    red = request.args.get('r')
    green = request.args.get('g')
    blue = request.args.get('b')

    missing_args = []
    if red is None:
        missing_args.append('r')
    if green is None:
        missing_args.append('g')
    if blue is None:
        missing_args.append('b')
    if len(missing_args) > 0:
        return "Missing required args: " + str(missing_args), status.HTTP_400_BAD_REQUEST

    red = int(red)
    green = int(green)
    blue = int(blue)

    resp = pipe_send(('set_color', Color(red, green, blue)))
    print(f'set_color({red}, {green}, {blue}): {resp}')

    if resp == led_control.CommandResponse.OK:
        return f'<!DOCTYPE html><html><head><style>body{{background-color:rgb({red},{green},{blue});}}</style></head><body></body></html>', status.HTTP_200_OK
    else:
        return 'oof', status.HTTP_500_INTERNAL_SERVER_ERROR


@app.route('/pattern/<path:pattern>')
def pattern_input(pattern: str):
    if pattern not in led_control.no_args_commands:
        return "Unknown pattern", status.HTTP_404_NOT_FOUND

    resp = pipe_send((pattern,))
    print(f'{pattern}(): {resp}')

    if resp == led_control.CommandResponse.OK:
        return '', status.HTTP_200_OK
    else:
        return '', status.HTTP_500_INTERNAL_SERVER_ERROR


@app.route('/')
def root():
    return app.send_static_file('index.html')


if __name__ == '__main__':
    parent_conn, child_conn = Pipe()
    p = Process(target=led_control.run_control_loop, args=(child_conn,))

    pipe = parent_conn

    p.start()
    app.run(host="0.0.0.0")
