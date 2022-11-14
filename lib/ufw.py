#!/usr/bin/env python3
from time import time
from sanic.log import logger
from subprocess import CalledProcessError, check_output, STDOUT

from lib.redis_client import redis_client

class Ufw(object):
    def clean(self):
        try:
            current_time = time()
            for key in redis_client.scan_iter("dynamic_ufw:*"):
                ip = key.split(":")[-1]
                rule = f"allow from {ip}"
                timestamp = float(redis_client.hget(key, "allow"))
                if current_time >= float(timestamp):
                    self.ufw_execute(f"delete {rule}")
                    redis_client.hdel(key, "allow")
                    logger.info(f"deleted rule\t {rule}")
                # else:
                #     logger.info(f"skipped rule\t {rule}")
        except CalledProcessError as error:
            logger.error("unable to execute ufw command: " + str(error))

    def add_rule(self, new_rule):
        try:
            self.ufw_execute(new_rule)
        except CalledProcessError as error:
            logger.error("unable to execute ufw command: " + str(error))

    def ufw_execute(self, rule):
        check_output("/usr/sbin/ufw " + rule, stderr = STDOUT, shell = True)
