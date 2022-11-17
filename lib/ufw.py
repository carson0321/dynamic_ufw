#!/usr/bin/env python3
from time import time
from sanic.log import logger
from subprocess import CalledProcessError, check_output, STDOUT

from lib.redis_client import redis_client

class Ufw(object):
    def clean(self):
        for key in redis_client.scan_iter("dynamic:ufw:*"):
            ip = key.split(":")[-1]
            rule = f"allow from {ip}"
            timestamp = float(redis_client.hget(key, "allow_ttl"))
            if time() >= float(timestamp):
                self.del_rule(rule)
                redis_client.hdel(key, "allow_ttl")
                logger.info(f"ufw deleted rule\t {rule}")
            # else:
            #     logger.info(f"ufw skipped rule\t {rule}")

    def add_rule(self, rule):
        try:
            self.execute(rule)
        except CalledProcessError as error:
            logger.error("unable to execute ufw command: " + str(error))

    def del_rule(self, rule):
        try:
            self.execute(f"delete {rule}")
        except CalledProcessError as error:
            logger.error("unable to execute ufw command: " + str(error))

    def execute(self, rule):
        return check_output("/usr/sbin/ufw " + rule, stderr = STDOUT, shell = True)
