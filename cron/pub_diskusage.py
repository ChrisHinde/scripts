#!/usr/local/bin/pyth

import subprocess
import json
import re

cmd = "mosquitto_pub"
topic = "system/stats/filesystem"

unit = 'h'

mem = subprocess.run(['df','-' + unit.lower()], capture_output=True, text=True)

for line in mem.stdout.splitlines():
    m = re.search(r'([\w\/]+)\s+([0-9.]+\w?)\s+([0-9.]+\w?)\s+([0-9.]+\w?)\s*([0-9]*\%)\s*([\/\w]*)', line)

    if m is not None:
        grps = m.groups()
        label = grps[5]

        data = { 'size': grps[1], 'used': grps[2], 'available': grps[3], 'used_perc': grps[4], 'mount': label, 'fs': grps[0] }

        if label == '/':
            label = '/ROOT'

        msg = json.dumps(data)
        subprocess.run([cmd,'-t',topic+label,'-m',msg])