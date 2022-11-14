#!/usr/bin/env python3
from os import path
from shutil import move
from sanic.log import logger
from datetime import datetime
from time import mktime, time
from parsedatetime import Calendar
from subprocess import CalledProcessError, check_output, STDOUT

class Ufw(object):
    RULES_FILE = '/usr/local/share/ufw-rules'
    TMP_RULES_FILE = '/tmp/ufw-rules'

    def clean(self):
        if path.exists(self.RULES_FILE):
            try:
                with open(self.TMP_RULES_FILE, 'a') as tmp_f:
                    current_time = time()
                    with open(self.RULES_FILE, 'r') as f:
                        for line in f.readlines():
                            timestamp, rule = line.strip("\n").split(' ', 1)
                            # Checks if rule has expired
                            if current_time < float(timestamp):
                                tmp_f.write(line)
                                # logger.info(self.str_time(time()) + "\tskipped rule\t" + rule)
                            else:
                                self.ufw_execute('delete ' + rule)
                                logger.info(self.str_time(time()) + "\tdeleted rule\t" + rule)
                move(self.TMP_RULES_FILE, self.RULES_FILE)

            except CalledProcessError as error:
                logger.error('unable to execute ufw command: ' + str(error))
            except IOError as error:
                logger.error('unable to read/write rules file: ' + str(error))

    def rule(self, new_rule, ttl):
        cal = Calendar()
        existed_rules = {}
        existed_rules[new_rule] = mktime(cal.parse(ttl)[0])
        try:
            if path.exists(self.RULES_FILE):
                for line in open(self.RULES_FILE, 'r'):
                    timestamp, rule = line.strip("\n").split(' ', 1)
                    if rule not in existed_rules:
                        existed_rules[rule] = float(timestamp)
                    # new rule exists in old table, update earliest timestamp
                    else:
                        if existed_rules[rule] > float(timestamp):
                            existed_rules[rule] = float(timestamp)
            with open(self.RULES_FILE, 'w') as f:
                for rule in existed_rules.keys():
                    f.write(str(existed_rules[rule]) + ' ' + rule + '\n')
            self.ufw_execute(new_rule)
        except CalledProcessError as error:
            logger.error('unable to execute ufw command: ' + str(error))
        except IOError:
            logger.error('unable to write rules file: ' + str(error))

    def str_time(self, time):
        return str(datetime.fromtimestamp(time))

    def ufw_execute(self, rule):
        check_output('/usr/sbin/ufw ' + rule, stderr = STDOUT, shell = True)
