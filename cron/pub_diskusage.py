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
combined_topic = Config.v('diskusage.combined_topic', '') # '/combined'
combined = {}

labels = Config.v('diskusage.labels', {})
strip_path = Config.v('diskusage.strip_path', False)

def get_label(label, fs):
    global combine, labels, strip_path

    if label in labels:
        label = labels[label]
    elif fs in labels:
        label = labels[fs]

    if label == '' or fs == 'total':
        label = '_TOTAL'

    if combine:
        if label == '/':
            label = '_ROOT'
    else:
        if label == '/':
            label = 'ROOT'

    if strip_path and '/' in label:
        _,label = label.rsplit('/',1)

    return label


if output_pure:
    unit = 'h'
    mem = subprocess.run(['df','-' + unit.lower()], capture_output=True, text=True)

    for line in mem.stdout.splitlines():
        m = re.search(r'([\w\/]+)\s+([0-9.]+\w?)\s+([0-9.]+\w?)\s+([0-9.]+\w?)\s*([0-9]*\%)\s*([\/\w]*)', line)

        if m is not None:
            grps = m.groups()
            mount = grps[5]
            fs = grps[0]

            if (mount in ignore) or (fs in ignore):
                continue

            label = get_label(mount, fs)

            data = { 'size': grps[1], 'used': grps[2], 'available': grps[3],
                     'used_perc': float(grps[4][:-1]), 'mount': mount, 'fs': fs, 'label': label }

            if not combine:
                t_label = '' if label == '_TOTAL' else '/' + label
                ex = Config.cmd('diskusage', topic + t_label, json.dumps(data))  # label already has a / prefix
                subprocess.run(ex)
            else:
                combined[label] = data

    if combine:
        ex = Config.cmd('diskusage', topic + combined_topic, json.dumps(combined))
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
            mount = grps[5]
            fs = grps[0]

            if (mount in ignore) or (fs in ignore):
                continue

            label = get_label(mount, fs)

            perc = round(float(grps[2]) / float(grps[1]) * 100.0, 2)
            data = { 'size': sizeof_fmt(grps[1]), 'used': sizeof_fmt(grps[2]), 'available': sizeof_fmt(grps[3]),
                     'used_perc': perc, 'used_p': float(grps[4][:-1]), 'mount': mount, 'fs': fs, 'label': label }

            if not combine:
                t_label = '' if label == '_TOTAL' else '/' + label
                ex = Config.cmd('diskusage', topic + t_label, json.dumps(data))  # label already has a / prefix
                subprocess.run(ex)
            else:
                combined[label] = data

    if combine:
        ex = Config.cmd('diskusage', topic + combined_topic, json.dumps(combined))
        subprocess.run(ex)