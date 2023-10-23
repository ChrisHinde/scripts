#!/usr/local/bin/pyth

import subprocess
import json
import re

cmd = "mosquitto_pub"
topic = "system/stats/memory/"

unit = 'M'

mem = subprocess.run(['free','-' + unit.lower()], capture_output=True, text=True)

for line in mem.stdout.splitlines():
    m = re.search(r'([\w:]*)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)\s*([0-9]*)\s*([0-9]*)\s*([0-9]*)', line)
    if m is not None:
        grps = m.groups()
        label = grps[0][:-1].lower()
        
        data = { 'total': int(grps[1]), 'used': int(grps[2]), 'free': int(grps[3]) }
        
        if label == 'mem':
            data['shared'] = int(grps[4])
            data['buff'] = int(grps[5])
            data['available'] = int(grps[6])

        msg = json.dumps(data)
        subprocess.run([cmd,'-t',topic+label,'-m',msg])