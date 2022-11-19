# Dynamic UFW

This project allows you to add ip to ufw (Uncomplicated Firewall) whitelist with a TTL(time to live). It saves into Redis and is designed as a socket server with a background scheduler to regularly refresh. It can set customized TTL (default 24 hours). After expiration time, the status will be cleared automatically. It also uses ipset to implement this, but the default uses ufw.

## Environment

* ufw 0.36 (`sudo apt install ufw`)
* redis 5.0.7 (`sudo apt install redis-server`)
* asdf 0.10.2
* python 3.10.8 (installed by asdf)
* poetry 1.2.2 (installed by asdf)
* ipset 7.5 (`sudo apt install ipset`)

## How to set up

* Open redis/ufw (`sudo systemctl start redis.service` and `sudo ufw enable`)
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
  * `sudo systemctl start dynamic-ufw.service`

  (Note: Rename working directory and install dependencies)

## How to use/test

* With default TTL (24 hours)
  * `curl --unix-socket /tmp/sanic.sock http://localhost/?ip=1.2.3.4`
  * `sudo ufw status`
* With customized TTL
  * `curl --unix-socket /tmp/sanic.sock "http://localhost/?ip=3.3.3.3&ex=10%20seconds"`
  * `sudo ufw status`

## Others

* Use ipset to allow IP
  * Create allowable IP list (`ipset create allowlist hash:ip hashsize 4096`)
  * Set default chain policies to deny all

    ```bash
    sudo iptables -P INPUT DROP
    sudo iptables -P FORWARD DROP
    sudo iptables -P OUTPUT ACCEPT
    ```

    Note: It will brutally cut all running connections including SSH. Only use this if you have access to a local console.

  * Add list into allowable permission

  ```bash
  sudo iptables -I INPUT -m set --match-set allowlist src -j ACCEPT
  sudo iptables -I FORWARD -m set --match-set allowlist src -j ACCEPT
  ```

  * (Optional) Destroy all chain policies

  ```bash
    sudo iptables -D INPUT -m set --match-set allowlist src -j ACCEPT
    sudo iptables -D FORWARD -m set --match-set allowlist src -j ACCEPT
    sudo ipset destroy allowlist
  ```

* `curl --unix-socket /tmp/sanic.sock "http://localhost/?ip=3.3.3.3&ex=30%20seconds&type=ipset"`
  * `sudo ipset list`
