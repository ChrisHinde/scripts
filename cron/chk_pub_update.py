#!/usr/local/bin/pyth

import subprocess

import os, sys
import datetime, time

cmd = "mosquitto_pub"
topic = "system/updates/apt/"

update_apt = False
output_upd = False

retain = True

retain_flag = '-r' if retain else ''

if os.geteuid() == 0:
    update_apt = True

if len(sys.argv) > 1:
    if sys.argv[1] == '--dont-update':
        update_apt = False
    if sys.argv[1] == '-v':
        output_upd = True

if update_apt:
    upd = subprocess.run(['apt','update'], capture_output=True, text=True)

    if output_upd:
        print(upd.stdout)

    os.environ['TZ'] = 'Europe/Stockholm'
    time.tzset()
    subprocess.run([cmd,'-t',topic+'last_updated','-m',str(datetime.datetime.now()), retain_flag])

chk = subprocess.run(['/usr/lib/update-notifier/apt-check'], capture_output=True, text=True)

(reg,sec) = chk.stderr.split(';')

subprocess.run([cmd,'-t',topic+'regular','-m',reg, retain_flag])
subprocess.run([cmd,'-t',topic+'security','-m',sec, retain_flag])
