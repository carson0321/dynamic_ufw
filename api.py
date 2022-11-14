#!/usr/bin/env python3
import socket
from lib.ufw import Ufw
from sanic import Sanic
from sanic.response import json
from os import unlink, path, chmod
from socket import error as socket_error
from apscheduler.schedulers.background import BackgroundScheduler
from socket import socket, AF_UNIX, AF_INET, SOCK_STREAM, inet_pton, inet_aton

ufw = Ufw()
sched = BackgroundScheduler()
app = Sanic(name="ufw")
server_socket = "/tmp/sanic.sock"

def listen_sock():
    if path.exists(server_socket):
        unlink(server_socket)
    sock = socket(AF_UNIX, SOCK_STREAM)
    sock.bind(server_socket)
    chmod(server_socket, 0o777)

    return sock

@app.route("/")
async def deny_ip(request):
    ip = request.args.get("ip")
    if not is_valid_ipv4_address(ip):
        return json({"error": "invalid IP"})
    ufw.rule(f"deny from {ip}", "24 hours")
    return json({"message": "OK"})

@app.main_process_stop
async def termination(app):
    unlink(server_socket)
    sched.shutdown()

def is_valid_ipv4_address(address):
    try:
        inet_pton(AF_INET, address)
    except AttributeError:
        try:
            inet_aton(address)
        except socket_error:
            return False
        return address.count('.') == 3
    except socket_error:
        return False

    return True

if __name__ == "__main__":
    sched.add_job(ufw.clean, "interval", seconds=1)
    sched.start()
    app.run(sock=listen_sock())
