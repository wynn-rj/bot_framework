import os
import json
import threading

class JsonConfigReader:
    _lock = threading.Lock()
    def __init__(self, file='config.json'):
        self._config_file = file
        self._data = None
        self._last_changed = 0
        version = os.getenv('PAMUS_BUILD')
        if version != 'release':
            version = 'dev'
        self._build = version
        self.update()

    def update(self):
        JsonConfigReader._lock.acquire()
        try:
            stamp = os.stat(self._config_file).st_mtime
            if stamp == self._last_changed:
                return
            self._last_changed = stamp
            with open(self._config_file, 'r') as config:
                self._data = json.load(config)
            data_clone = dict(self._data)
            for key, value in self._data.items():
                if isinstance(value, dict) and 'release' in value \
                        and 'dev' in value:
                    data_clone[key] = self._data[key][self._build]
            self.__dict__.update(data_clone)
        finally:
            JsonConfigReader._lock.release()

    def save(self):
        JsonConfigReader._lock.acquire()
        try:
            for key, value in self._data.items():
                if isinstance(value, dict) and 'release' in value \
                        and 'dev' in value:
                    self._data[key][self._build] = self.__dict__[key]
                else:
                    self._data[key] = self.__dict__[key]
            with open(self._config_file, 'w') as config:
                json.dump(self._data, config, sort_keys=True,
                          indent=4, separators=(',', ': '))
        finally:
            JsonConfigReader._lock.release()
