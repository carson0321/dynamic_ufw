# Dynamic UFW

This script allows you to add rules to ufw (Uncomplicated Firewall) with a time to live. It uses `/usr/local/share/ufw-rules` file to save the rules. I design a socket server with a background scheduler to regularly refresh.

## Environment

* asdf 0.10.2
* python 3.10.8 (installed by asdf)
* poetry 1.2.2 (installed by asdf)

## How to use

* Use general user to install dependencies
  1. `poetry config virtualenvs.in-project true`
  2. `poetry env use python`
  3. `poetry install`

* Use root to set up
  1. `source .venv/bin/activate`
  2. `python api.py`

* `curl --unix-socket /tmp/sanic.sock http://localhost/?ip=1.2.3.4`
