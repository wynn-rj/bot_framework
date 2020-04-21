import os
import json
import threading

class JsonConfigReader:
    _lock = threading.Lock()
    def __init__(self, file='config.json'):
        self._config_file = file
        self._data = None
        self._last_changed = 0
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
            self.__dict__.update(self._data)
        finally:
            JsonConfigReader._lock.release()

    def save(self):
        JsonConfigReader._lock.acquire()
        try:
            for k in self._data.keys():
                self._data[k] = self.__dict__[k]
            with open(self._config_file, 'w') as config:
                json.dump(self._data, config, sort_keys=True,
                          indent=4, separators=(',', ': '))
        finally:
            JsonConfigReader._lock.release()
