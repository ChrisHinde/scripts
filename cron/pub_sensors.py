#!/usr/local/bin/pyth

import subprocess
import re

cmd = "mosquitto_pub"
topic = "system/sensors/temperatures/"

sens = subprocess.run(['sensors'], capture_output=True, text=True)

for line in sens.stdout.splitlines():
    if line.find('C ') > 0:
        f = re.search(r'([\w\s]+):\s+(\+[0-9]+[.][0-9]+)', line)

        id = f.groups()[0]
        temp = f.groups()[1]

        id = re.sub(r'(\s+[id]*\s?)', '_', id)

        subprocess.run([cmd,'-t',topic+id,'-m',temp])