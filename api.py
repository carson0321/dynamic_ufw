#!/usr/bin/env python3

import socket
from sanic import Sanic
from sanic.response import json
from os import unlink, path, chmod
from socket import error as socket_error
from subprocess import CalledProcessError, check_output, STDOUT
from apscheduler.schedulers.background import BackgroundScheduler
from socket import socket, AF_UNIX, AF_INET, SOCK_STREAM, inet_pton, inet_aton

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
    add_ufw_deny_rule(ip)
    return json({"message": "OK"})

@app.main_process_stop
async def termination(app):
    unlink(server_socket)
    sched.shutdown()

def add_ufw_deny_rule(ip):
    try:
        check_output(f"python ufw.py --rule 'deny from {ip}'", stderr = STDOUT, shell = True)
    except CalledProcessError as error:
        print(error)

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

def clean_ufw_expired_rules():
    try:
        check_output("python ufw.py --clean", stderr = STDOUT, shell = True)
    except CalledProcessError as error:
        print(error)

if __name__ == "__main__":
    sched.add_job(clean_ufw_expired_rules, "interval", seconds=1)
    sched.start()
    app.run(sock=listen_sock())
