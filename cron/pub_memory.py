#!/usr/local/bin/pyth

import subprocess
import json
import re

from config import Config

topic = Config.t('memory','stats/memory')

unit = Config.v('memory.unit', 'M')
pub_ratio = Config.v('memory.pub_used_ratio', True)
pub_perc = Config.v('memory.pub_used_percentage', True)
combine = Config.v('memory.combine', False)
combined = {}

retain = Config.v('memory.retain', False)

mem = subprocess.run(['free','-' + unit.lower()], capture_output=True, text=True)

for line in mem.stdout.splitlines():
    m = re.search(r'([\w:]*)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)\s*([0-9]*)\s*([0-9]*)\s*([0-9]*)', line)
    if m is not None:
        grps = m.groups()
        label = grps[0][:-1].lower()
        
        data = { 'total': int(grps[1]), 'used': int(grps[2]), 'free': int(grps[3]), 'unit': unit }
        if pub_ratio:
            data['used_ratio'] = round(data['used'] / data['total'], 5)
        if pub_perc:
            data['used_perc'] = round(data['used_ratio'] * 100, 1)

        if label == 'mem':
            data['shared'] = int(grps[4])
            data['buff'] = int(grps[5])
            data['available'] = int(grps[6])

        if combine:
            combined[label] = data
        else:
            ex = Config.cmd('memory', topic + '/' + label, json.dumps(data))
            subprocess.run(ex)

if combined:
    ex = Config.cmd('memory', topic, json.dumps(data))
    subprocess.run(ex)