#!/usr/bin/env python3
from argparse import ArgumentParser
from datetime import datetime
from os import getpid, makedirs, path, remove
from parsedatetime import Calendar
from shutil import move
from subprocess import CalledProcessError, check_output, STDOUT
from sys import exit
from time import mktime, time


class Ufw(object):
    PID_FILE = '/var/run/ufw-rules.pid'
    RULES_FILE = '/usr/local/share/ufw-rules'
    TMP_RULES_FILE = '/tmp/ufw-rules'

    def status(self):
        if path.exists(self.RULES_FILE):
            try:
                print("Expiration\t\tRule")
                print('=' * 80)

                # Loops through the rules lines
                for line in open(self.RULES_FILE, 'r'):
                    # Breaks apart line into expiration timestamp and rule
                    timestamp, rule = line.strip("\n").split(' ', 1)
                    print(self.str_time(float(timestamp)) + "\t" + rule)
            except IOError:
                self.error('unable to read from the rules file: ' + self.RULES_FILE)
        else:
            self.error('there are no rules to display')

    def clean(self):
        # Checks for PID file
        if path.exists(self.PID_FILE):
            self.error('ufw-rules is already running')
        else:
            # Creates the PID file
            try:
                with open(self.PID_FILE, 'w') as f:
                    f.write(str(getpid()))
            except IOError:
                self.error('unable to create PID file: ' + self.PID_FILE)

            # Checks for the rules file
            if path.exists(self.RULES_FILE):
                # Opens the temporary rules file
                try:
                    with open(self.TMP_RULES_FILE, 'a') as tmp_f:
                        current_time = time()
                        # Loops through the rules lines
                        for line in open(self.RULES_FILE, 'r'):
                            # Breaks apart line into expiration timestamp and rule
                            timestamp, rule = line.strip("\n").split(' ', 1)

                            # Checks if rule has expired
                            if current_time < float(timestamp):
                                tmp_f.write(line)
                                print(self.str_time(time()) + "\tskipped rule\t" + rule)
                            else:
                                self.ufw_execute('delete ' + rule)
                                print(self.str_time(time()) + "\tdeleted rule\t" + rule)
                    # Moves the tmp file to the rules file
                    move(self.TMP_RULES_FILE, self.RULES_FILE)

                except CalledProcessError as error:
                    self.ufw_error(error)

                except IOError:
                    self.error('unable to read/write rules file')

                # Removes the PID
                remove(self.PID_FILE)

    def rule(self, rule, ttl):
        # Converts the TTL to a timestamp
        cal = Calendar()
        timestamp = mktime(cal.parse(ttl)[0])

        # Writes the rule to the rules file
        try:
            with open(self.RULES_FILE, 'a') as f:
                f.write(str(timestamp) + ' ' + rule + '\n')
            self.ufw_execute(rule)
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
