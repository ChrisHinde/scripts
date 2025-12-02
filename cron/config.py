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
        if not isinstance(obj, dict):
            if debug:
                print("[Config::_find] Given object to look in is not valid!")
            return None

        keys = path.split('.')
        rv = obj
        last_key = '/'

        for key in keys:
            if not isinstance(rv, dict):
                if debug:
                    print("[Config::_find] Looking for '", key, "' but '", last_key, "' isn't a dict, can't go further! [path='",path,"']", sep='')
                return None
            elif key in rv:
                rv = rv[key]
            else:
                if debug:
                    print("[Config::_find] Couldn't find '", key, "' [path='", path, "']", sep='')
                return None

            last_key = key

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

    print("\nFind MQTT prefix value:")
    print(Config.v('mqtt.prefix', 'mqtt_test'))
    print("\nFind MQTT prefix topic:")
    print(Config.t('mqtt.prefix', 'mqtt_topic_test'))
    print("\nFind apt topic:")
    print(Config.t('apt', 'apt_topic_test'))
    print("\nFind non existing topic:")
    print(Config.t('#NULL#', 'null_topic_test'))
    print("\nFind non existing apt topic:")
    print(Config.t('apt.does_not_exist', 'apt_nothing_topic_test'))
    print("\nFind non existing mqtt value:")
    print(Config.v('mqtt.does_not_exist', 'mqtt_nothing_test'))
    print("\nFind non existing mqtt sub value:")
    print(Config.v('mqtt.cmd_pub.does_not_exist', 'mqtt_nothing_sub_test'))