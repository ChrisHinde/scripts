#!/usr/local/bin/pyth

import subprocess
import json
import re

from config import Config

topic = Config.t('diskusage','stats/filesystem')

output_pure = Config.v('diskusage.output_pure', False)
output_bytes = Config.v('diskusage.output_bytes', True)

ignore = Config.v('diskusage.ignore', [])

combine = Config.v('diskusage.combine', True)
combined = {}

if output_pure:
    unit = 'h'
    mem = subprocess.run(['df','-' + unit.lower()], capture_output=True, text=True)

    for line in mem.stdout.splitlines():
        m = re.search(r'([\w\/]+)\s+([0-9.]+\w?)\s+([0-9.]+\w?)\s+([0-9.]+\w?)\s*([0-9]*\%)\s*([\/\w]*)', line)

        if m is not None:
            grps = m.groups()
            label = grps[5]

            if (label in ignore) or (grps[0] in ignore):
                continue

            data = { 'size': grps[1], 'used': grps[2], 'available': grps[3], 'used_perc': float(grps[4][:-1]), 'mount': label, 'fs': grps[0] }

            if not combine:
                if label == '/':
                    label = '/ROOT'

                ex = Config.cmd('memory', topic + label, json.dumps(data))  # label already has a / prefix
                subprocess.run(ex)
            else:
                if label == '':
                    label = '#TOTAL'
                elif label == '/':
                    label = '#ROOT'
                combined[label] = data

    if combine:
        ex = Config.cmd('memory', topic + '/combined', json.dumps(combined))
        subprocess.run(ex)

    topic = topic + '_b'

if output_bytes:
    def sizeof_fmt(num, suffix="B"):
        num = int(num)
        for unit in ("Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
            if abs(num) < 1024.0:
                return f"{num:3.1f}{unit}{suffix}"
            num /= 1024.0
        return f"{num:.1f}Yi{suffix}"

    mem = subprocess.run(['df','--total'], capture_output=True, text=True)
    combined = {}

    for line in mem.stdout.splitlines():
        m = re.search(r'([\w\/]+)\s+([0-9.]+\w?)\s+([0-9.]+\w?)\s+([0-9.]+\w?)\s*([0-9]*\%)\s*([\/\w]*)', line)

        if m is not None:
            grps = m.groups()
            label = grps[5]

            if (label in ignore) or (grps[0] in ignore):
                continue

            perc = round(float(grps[2]) / float(grps[1]) * 100.0, 2)
            data = { 'size': sizeof_fmt(grps[1]), 'used': sizeof_fmt(grps[2]), 'available': sizeof_fmt(grps[3]), 'used_perc': perc, 'used_p': float(grps[4][:-1]), 'mount': label, 'fs': grps[0] }

            if not combine:
                if label == '/':
                    label = '/ROOT'

                ex = Config.cmd('memory', topic + label, json.dumps(data))  # label already has a / prefix
                subprocess.run(ex)
            else:
                if label == '':
                    label = '#TOTAL'
                elif label == '/':
                    label = '#ROOT'
                combined[label] = data

    if combine:
        ex = Config.cmd('memory', topic + '/combined', json.dumps(combined))
        subprocess.run(ex)