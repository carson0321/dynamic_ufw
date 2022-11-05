import sys
import socket
import os
from sanic import Sanic
from sanic.response import json


server_socket = '/tmp/sanic.sock'
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.bind(server_socket)
app = Sanic(name='ufw')


@app.route("/")
async def test(request):
    return json({"hello": "world"})

@app.listener("main_process_stop")
async def termination(app, loop):
    os.unlink(server_socket)

if __name__ == "__main__":
    app.run(sock=sock)
