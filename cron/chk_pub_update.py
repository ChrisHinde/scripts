#!/usr/local/bin/pyth

import subprocess
import re, json
import os, sys
import datetime, time

debug = False

from config import Config

topic = Config.t('apt','updates/apt') + '/'

dir_path = os.path.dirname(os.path.realpath(__file__)) + '/'

update_apt = Config.v('apt.run_update', False)
force_no_upd = Config.v('apt.force_no_update', True)
combine = Config.v('apt.combine', False)
output_upd = False

if os.geteuid() == 0 and not force_no_upd:
    update_apt = True

if len(sys.argv) > 1:
    if '--dont-update' in sys.argv:
        update_apt = False
    if '--update' in sys.argv:
        update_apt = True
    if '-u' in sys.argv:
        update_apt = True
    if '-v' in sys.argv:
        output_upd = True
    if '-d' in sys.argv:
        debug = True

reg = 0
sec = None
packages = None
last_updated = None

if update_apt:
    upd = subprocess.run(['apt','update'], capture_output=True, text=True)
    out = upd.stdout

    re_s = re.search('([0-9]+) packages can be upgraded', out)
    packages = re_s.group(1)

    if output_upd:
        print(out)

    if upd.returncode != 0:
        print("Upd failed")
        print(out)
        exit(1)

    os.environ['TZ'] = 'Europe/Stockholm'
    time.tzset()
    last_updated = str(datetime.datetime.now())

    if combine is False or combine == 'both':
        ex = Config.cmd('apt', topic + 'last_updated', last_updated)
        if debug:
            print(ex)
        subprocess.run(ex)

proc = '/usr/lib/update-notifier/apt-check'

if os.path.isfile(proc):
    chk = subprocess.run(proc, capture_output=True, text=True)
    (reg,sec) = chk.stderr.split(';')
else:
    proc = dir_path + 'get-upd.sh'
    chk = subprocess.run(proc, capture_output=True, text=True)
    reg = chk.stdout.strip()

if combine is False or combine == 'both':
    ex = Config.cmd('apt', topic + 'regular', reg)
    if debug:
        print(ex)

    subprocess.run(ex)

    if sec is not None:
        ex = Config.cmd('apt', topic + 'security', sec)
        if debug:
            print(ex)
        subprocess.run(ex)

    if packages is not None:
        ex = Config.cmd('apt', topic + 'packages', packages)
        if debug:
            print(ex)
        subprocess.run(ex)

if combine is True or combine == 'both':
    data = {
        'regular': reg
    }
    if sec is not None:
        data['security'] = sec
    if packages is not None:
        data['packages'] = packages
    
    if last_updated is not None:
        data['last_updated'] = last_updated

    ex = Config.cmd('apt', topic[:-1], json.dumps(data))
    if debug:
        print(ex)

    subprocess.run(ex)