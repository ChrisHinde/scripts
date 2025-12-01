import yaml
import os
from os.path import isfile,join,splitext

debug = False

if __name__ == "__main__":
    debug = True


wd = os.path.dirname(os.path.realpath(__file__)) + '/'
conf_path = '../'
conf_files = ['config.yml', 'config-default.yml']

class Config:
    c = {}
    conf_file = None

    def init():
        for cf in conf_files:
            f = join(wd, conf_path, cf)
            if isfile(f):
                Config.conf_file = f
                break

        if Config.conf_file is None:
            print("ERROR: No config file found!")
            print("  Looked for", conf_files, "in", conf_path)
            exit(1)

        _, ext = splitext(Config.conf_file)
        if ext != '.yml':
            print(Config.conf_file, "is not a .yml")
            exit()

        with open(Config.conf_file) as stream:
            try:
                Config.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(f)
                print(exc)
                exit()

    def _find(path, obj):
        keys = path.split('.')
        rv = obj
        for key in keys:
            if key in rv:
                rv = rv[key]
            else:
                if debug:
                    print("Couldn't find the key for", path)
                return None
        return rv

    def get(path, default=None):
        val = Config._find(path, Config.config)
        if val is None:
            return default
        else:
            return val
    def v(path, default=None):
        return Config.get(path, default)

    def topic(part, default=''):
        prefix = Config.get('mqtt.prefix')
        top = Config.get(part + '.topic', default)

        if prefix:
            return prefix + top
        else:
            return top
    def t(part, default=''):
        return Config.topic(part, default)
    
    def cmd(part, topic, msg, retain = None):
        if retain is None:
            retain = Config.v(part + '.retain', Config.v('mqtt.default.retain', False))

        c = Config.v('mqtt.cmd_pub','mosquitto_pub')

        args = [c, '-t', topic, '-m', msg]
        if retain:
            args.append('-r')
        return args

Config.init()

if __name__ == "__main__":
    print("Config test")

    if debug:
        print("Using", Config.conf_file)
        print(Config.config)

    print(Config.v('mqtt.prefix', 'mqtt_test'))
    print(Config.t('apt', 'apt_topic_test'))
    print(Config.t('#NULL#', 'null_topic_test'))