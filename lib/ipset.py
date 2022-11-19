#!/usr/bin/env python3
from time import time
from sanic.log import logger
from subprocess import CalledProcessError, check_output, STDOUT

from lib.redis_client import redis_client

class Ipset(object):
    def clean(self):
        for key in redis_client.scan_iter("dynamic:ipset:*"):
            ip = key.split(":")[-1]
            timestamp = float(redis_client.hget(key, "allow_ttl"))
            if time() >= float(timestamp):
                try:
                    self.execute(f"del allowlist {ip}")
                    redis_client.hdel(key, "allow_ttl")
                    logger.info(f"ipset deleted ip\t {ip}")
                except CalledProcessError as error:
                    logger.error("unable to execute ipset command: " + str(error))
            # else:
            #     logger.info(f"ipset skipped ip\t {ip}")

    def add_ip(self, ip):
        try:
            self.execute(f"add allowlist {ip}")
        except CalledProcessError as error:
            logger.error("unable to execute ipset command: " + str(error))

    def execute(self, rule):
        return check_output("/usr/sbin/ipset " + rule, stderr = STDOUT, shell = True)
