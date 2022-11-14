# Dynamic UFW

This script allows you to add rules to UFW (Uncomplicated Firewall) with a TTL(time to live). It's saved into Redis, and designed as a socket server with a background scheduler to regularly refresh. After TTL, the status will be cleared.

## Environment

* ufw 0.36
* redis 5.0.7
* asdf 0.10.2
* python 3.10.8 (installed by asdf)
* poetry 1.2.2 (installed by asdf)

## How to use

* Console:
  * Use general user to install dependencies
    1. `poetry config virtualenvs.in-project true`
    2. `poetry env use python`
    3. `poetry install`

  * Use root to set up
    1. `source .venv/bin/activate`
    2. `python api.py`

* Systemd
  * copy `misc/dynamic-ufw.service` to `/etc/systemd/system/`
  * `systemctl start dynamic-ufw.service`

  (Note: rename working directory and install dependencies)

## How to test

* With default TTL (24 hours)
  * `curl --unix-socket /tmp/sanic.sock http://localhost/?ip=1.2.3.4`
  * `sudo ufw status`
* With customized TTL
  * `curl --unix-socket /tmp/sanic.sock "http://localhost/?ip=3.3.3.3&ex=10%20seconds"`
  * `sudo ufw status`
