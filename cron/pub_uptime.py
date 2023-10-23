#!/usr/local/bin/pyth

import subprocess
import json
import re

cmd = "mosquitto_pub"
topic_usg = "system/stats/usage"
topic_upt = "system/stats/uptime"

up = subprocess.run(['uptime'], capture_output=True, text=True)

u = re.search(r'up (.*), (\d+) users,[\w\s]+:\s+([0-9]+[.][0-9]+)*,\s+([0-9]+[.][0-9]+)*,\s+([0-9]+[.][0-9]+)*', up.stdout)

if u is not None:
    grps = u.groups()

    upt = { 'uptime': grps[0], 'users': grps[1] }
    usg = { '1min': grps[2], '5min': grps[3], '15min': grps[4] }

    msg = json.dumps(usg)
    subprocess.run([cmd,'-t',topic_usg,'-m',msg])

    msg = json.dumps(upt)
    subprocess.run([cmd,'-t',topic_upt,'-m',msg])