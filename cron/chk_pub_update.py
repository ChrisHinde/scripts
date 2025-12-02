#!/usr/local/bin/pyth

import subprocess

import os, sys
import datetime, time

debug = False

from config import Config

topic = Config.t('apt','updates/apt') + '/'

dir_path = os.path.dirname(os.path.realpath(__file__)) + '/'

update_apt = Config.v('apt.run_update', False)
force_no_upd = Config.v('apt.force_no_update', True)
output_upd = False

if os.geteuid() == 0 and not force_no_upd:
    update_apt = True

if len(sys.argv) > 1:
    if sys.argv[1] == '--dont-update':
        update_apt = False
    if sys.argv[1] == '--update':
        update_apt = True
    if sys.argv[1] == '-u':
        update_apt = True
    if sys.argv[1] == '-v':
        output_upd = True
    if sys.argv[1] == '-d':
        debug = True

if update_apt:
    upd = subprocess.run(['apt','update'], capture_output=True, text=True)

    if output_upd:
        print(upd.stdout)

    os.environ['TZ'] = 'Europe/Stockholm'
    time.tzset()
    ex = Config.cmd('apt', topic + 'last_updated', str(datetime.datetime.now()))
    if debug:
        print(ex)
    subprocess.run(ex)

reg = 0
sec = None
proc = '/usr/lib/update-notifier/apt-check'

if os.path.isfile(proc):
    chk = subprocess.run(proc, capture_output=True, text=True)
    (reg,sec) = chk.stderr.split(';')
else:
    proc = dir_path + 'get-upd.sh'
    chk = subprocess.run(proc, capture_output=True, text=True)
    reg = chk.stdout.strip()

ex = Config.cmd('apt', topic + 'regular', reg)
if debug:
    print(ex)

subprocess.run(ex)

if sec is not None:
    ex = Config.cmd('apt', topic + 'security', sec)
    if debug:
        print(ex)
    subprocess.run(ex)
