#!/usr/local/bin/pyth

import subprocess
import json
import re

pub_individually = False
combined = {}

cmd = "mosquitto_pub"
topic = "system/stats/filesystem"

output_pure = False
output_bytes = True

ignore = ['tmpfs','efivarfs', '/boot/efi']

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

            if pub_individually:
                if label == '/':
                    label = '/ROOT'

                msg = json.dumps(data)
                subprocess.run([cmd,'-t',topic+label,'-m',msg])
            else:
                if label == '':
                    label = '#TOTAL'
                elif label == '/':
                    label = '#ROOT'
                combined[label] = data

    if not pub_individually:
        msg = json.dumps(combined)
        subprocess.run([cmd,'-t',topic+'/combined','-m',msg])

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

            if pub_individually:
                if label == '/':
                    label = '/ROOT'

                msg = json.dumps(data)
                subprocess.run([cmd,'-t',topic+label,'-m',msg])
            else:
                if label == '':
                    label = '#TOTAL'
                elif label == '/':
                    label = '#ROOT'
                combined[label] = data

    if not pub_individually:
        msg = json.dumps(combined)
        subprocess.run([cmd,'-t',topic+'/combined','-m',msg])