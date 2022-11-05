#!/usr/bin/env python3

from sys import exit
from shutil import move
from datetime import datetime
from time import mktime, time
from parsedatetime import Calendar
from argparse import ArgumentParser
from os import getpid, makedirs, path, remove
from subprocess import CalledProcessError, check_output, STDOUT


class Ufw(object):
    PID_FILE = '/var/run/ufw-rules.pid'
    RULES_FILE = '/usr/local/share/ufw-rules'
    TMP_RULES_FILE = '/tmp/ufw-rules'

    def status(self):
        if path.exists(self.RULES_FILE):
            try:
                print("Expiration\t\tRule")
                print('=' * 80)

                for line in open(self.RULES_FILE, 'r'):
                    timestamp, rule = line.strip("\n").split(' ', 1)
                    print(self.str_time(float(timestamp)) + "\t" + rule)
            except IOError:
                self.error('unable to read from the rules file: ' + self.RULES_FILE)
        else:
            self.error('there are no rules to display')

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
        exit(2)

    def str_time(self, time):
        return str(datetime.fromtimestamp(time))

    def ufw_execute(self, rule):
        check_output('ufw ' + rule, stderr = STDOUT, shell = True)

    def ufw_error(self, error):
        self.error('ufw: ' + error.output.decode(encoding = 'UTF-8'))


if __name__ == '__main__':
    parser = ArgumentParser(description = 'Apply `ufw` rules with TTL')
    parser.add_argument('-s', '--status', action = 'store_true', help = 'show rule list with expirations')
    parser.add_argument('-c', '--clean', action = 'store_true', help = 'clean up expired rules')
    parser.add_argument('-r', '--rule', help = 'rule to be added to `ufw`')
    parser.add_argument('-t', '--ttl', default = '24 hours', help = 'time to live for the rule')
    args = parser.parse_args()

    ufw = Ufw()
    if args.status:
        ufw.status()
    elif args.clean:
        ufw.clean()
    elif args.rule:
        ufw.rule(args.rule, args.ttl)
    else:
        parser.print_help()
