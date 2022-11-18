#!/usr/bin/env python3
import redis
import socket
from time import mktime
from sanic import Sanic
from sanic.log import logger
from sanic.response import json
from parsedatetime import Calendar
from os import unlink, path, chmod
from socket import error as socket_error
from apscheduler.schedulers.background import BackgroundScheduler
from socket import socket, AF_UNIX, AF_INET, SOCK_STREAM, inet_pton, inet_aton

from lib.ufw import Ufw
from lib.ipset import Ipset
from lib.redis_client import redis_client

ufw = Ufw()
ipset = Ipset()
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
async def allow_ip(request):
    try:
        redis_client.ping()
    except redis.ConnectionError:
        return json({"error": "redis connection refused"})

    ip = request.args.get("ip")
    if not is_valid_ipv4_address(ip):
        return json({"error": "invalid IP"})

    # expired time (rule's TTL)
    ex = "24 hours"
    if request.args.get("ex") is not None:
        ex = request.args.get("ex")
    # set now when parsing failed
    timestamp = mktime(Calendar().parse(ex)[0])

    if request.args.get("type") == "ipset":
        redis_key = f"dynamic:ipset:{ip}"
        if not redis_client.hexists(redis_key, "allow_ttl"):
            ipset.add_ip(ip)
    # default use ufw
    else:
        redis_key = f"dynamic:ufw:{ip}"
        if not redis_client.hexists(redis_key, "allow_ttl"):
            ufw.add_rule(f"allow from {ip}")
    redis_client.hset(redis_key, "allow_ttl", str(timestamp))

    logger.info(f"add 'allow from {ip}' with {ex} successfully")
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
    sched.add_job(ufw.clean, "interval", seconds=1, max_instances=1)
    sched.add_job(ipset.clean, "interval", seconds=1, max_instances=1)
    sched.start()
    app.run(sock=listen_sock())
