import os
import copy
import threading
import types
import yaml

class YAMLConfigReader:
    _lock = threading.Lock()
    def __init__(self, file='/config/config.yml', defaults=None):
        self._config_file = file
        if not os.path.exists(file):
            with open(file, 'a'):
                pass
        self._data = None
        self._last_changed = 0
        self.defaults = defaults or {}
        build = os.getenv('BUILD', 'release')
        if build != 'dev':
            build = 'release'
        self._build = build
        self.data = None
        self.update()

    def update(self):
        YAMLConfigReader._lock.acquire()
        try:
            stamp = os.stat(self._config_file).st_mtime
            if stamp == self._last_changed:
                return
            self._last_changed = stamp
            with open(self._config_file, 'r') as config:
                self._data = yaml.safe_load(config) or dict()
            data_clone = copy.deepcopy(self.defaults)
            data_clone.update(self._data)
            for key, value in self._data.items():
                if isinstance(value, dict) and 'release' in value \
                        and 'dev' in value:
                    data_clone[key] = self._data[key][self._build]
            self.data = types.SimpleNamespace(**data_clone)
        finally:
            YAMLConfigReader._lock.release()

    def save(self):
        YAMLConfigReader._lock.acquire()
        try:
            for key, value in vars(self.data).items():
                if key in self.defaults and self.defaults[key] == value:
                    continue
                cur_val = None if not key in self._data else self._data[key]
                if isinstance(cur_val, dict) and 'release' in cur_val \
                        and 'dev' in cur_val:
                    self._data[key][self._build] = value
                else:
                    self._data[key] = value
            with open(self._config_file, 'w') as config:
                yaml.dump(self._data, config, default_flow_style=False)
        finally:
            YAMLConfigReader._lock.release()
