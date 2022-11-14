#!/usr/bin/env python3
from shutil import move
from datetime import datetime
from time import mktime, time
from parsedatetime import Calendar
from os import getpid, path, remove
from subprocess import CalledProcessError, check_output, STDOUT

class Ufw(object):
    PID_FILE = '/var/run/ufw-rules.pid'
    RULES_FILE = '/usr/local/share/ufw-rules'
    TMP_RULES_FILE = '/tmp/ufw-rules'

    def clean(self):
        if path.exists(self.PID_FILE):
            self.error('ufw-rules is already running')
        else:
            try:
                with open(self.PID_FILE, 'w') as f:
                    f.write(str(getpid()))
            except IOError:
                self.error('unable to create PID file: ' + self.PID_FILE)

            if path.exists(self.RULES_FILE):
                try:
                    with open(self.TMP_RULES_FILE, 'a') as tmp_f:
                        current_time = time()
                        for line in open(self.RULES_FILE, 'r'):
                            timestamp, rule = line.strip("\n").split(' ', 1)

                            # Checks if rule has expired
                            if current_time < float(timestamp):
                                tmp_f.write(line)
                                print(self.str_time(time()) + "\tskipped rule\t" + rule)
                            else:
                                self.ufw_execute('delete ' + rule)
                                print(self.str_time(time()) + "\tdeleted rule\t" + rule)
                    move(self.TMP_RULES_FILE, self.RULES_FILE)

                except CalledProcessError as error:
                    self.ufw_error(error)

                except IOError:
                    self.error('unable to read/write rules file')

            remove(self.PID_FILE)

    def rule(self, new_rule, ttl):
        cal = Calendar()
        existed_rules = {}
        existed_rules[new_rule] = mktime(cal.parse(ttl)[0])
        try:
            self.ufw_execute(new_rule)
            if path.exists(self.RULES_FILE):
                for line in open(self.RULES_FILE, 'r'):
                    timestamp, rule = line.strip("\n").split(' ', 1)
                    if rule not in existed_rules:
                        existed_rules[rule] = float(timestamp)
                    else:
                        if existed_rules[rule] < float(timestamp):
                            existed_rules[new_rule] = float(timestamp)

            with open(self.RULES_FILE, 'w') as f:
                for rule in existed_rules.keys():
                    f.write(str(existed_rules[rule]) + ' ' + rule + '\n')
        except CalledProcessError as error:
            self.ufw_error(error)
        except IOError:
            self.error('unable to write rules file')

    def error(self, message):
        print('errors: ' + message)

    def str_time(self, time):
        return str(datetime.fromtimestamp(time))

    def ufw_execute(self, rule):
        check_output('ufw ' + rule, stderr = STDOUT, shell = True)

    def ufw_error(self, error):
        self.error('ufw: ' + error.output.decode(encoding = 'UTF-8'))
