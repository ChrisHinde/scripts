#!/usr/local/bin/pyth

import subprocess
import json
import re   

from config import Config

topic = Config.t('sensors','sensors/temperatures')
combine = Config.v('sensors.combine', True)
combined = {}

sens = subprocess.run(['sensors'], capture_output=True, text=True)

for line in sens.stdout.splitlines():
    if line.find('C ') > 0:
        s = re.search(r'([\w\s]+):\s+(\+[0-9]+[.][0-9]+)', line)

        id = s.groups()[0]
        temp = float(s.groups()[1])

        id = re.sub(r'(\s+[id]*\s?)', '_', id)

        if combine:
            combined[id] = temp
        else:
            ex = Config.cmd('sensors', topic + '/' + id, str(temp))
            subprocess.run(ex)

if combine:
    ex = Config.cmd('sensors', topic + '/combined', json.dumps(combined))
    subprocess.run(ex)