#!/usr/local/bin/pyth

import subprocess
import json
import re

pub_individually = False

cmd = "mosquitto_pub"
topic = "system/sensors/temperatures/"

data = {}

sens = subprocess.run(['sensors'], capture_output=True, text=True)

for line in sens.stdout.splitlines():
    if line.find('C ') > 0:
        s = re.search(r'([\w\s]+):\s+(\+[0-9]+[.][0-9]+)', line)

        id = s.groups()[0]
        temp = float(s.groups()[1])

        id = re.sub(r'(\s+[id]*\s?)', '_', id)

        data[id] = temp

        if pub_individually:
            subprocess.run([cmd,'-t',topic+id,'-m',str(temp)])

data_s = json.dumps(data)
subprocess.run([cmd,'-t',topic+'combined','-m', data_s ])