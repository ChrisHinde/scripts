#!/usr/local/bin/pyth

import subprocess
import json
import re

from config import Config

topic_usg = Config.t('uptime.usage','stats/usage')
topic_upt = Config.t('uptime.uptime','stats/uptime')

up = subprocess.run(['uptime'], capture_output=True, text=True)

u = re.search(r'up (.*),\s+(\d+) user[s]?,[\w\s]+:\s+([0-9]+[.][0-9]+)*,\s+([0-9]+[.][0-9]+)*,\s+([0-9]+[.][0-9]+)*', up.stdout)

if u is not None:
    grps = u.groups()

    upt = { 'uptime': grps[0].replace('  ',' '), 'users': grps[1] }
    usg = { '1min': float(grps[2]), '5min': float(grps[3]), '15min': float(grps[4]) }

    ex = Config.cmd('uptime', topic_upt, json.dumps(upt))
    subprocess.run(ex)

    ex = Config.cmd('uptime', topic_usg, json.dumps(usg))
    subprocess.run(ex)
else:
    print("Uptime ERROR")
    exit(1)
