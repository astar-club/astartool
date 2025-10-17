import collections

from astartool.setuptool import PY310

if PY310:
    from collections.abc import MutableMapping
else:
    from collections import MutableMapping
from functools import reduce


class MergeMap(MutableMapping):
    def __init__(self, values=None, callback=None):
        super().__init__()
        self.__inner = collections.defaultdict(list)
        if values is not None:
            for k, v in values.items():
                self.__inner[k].append(v)
        if callback is None:
            self.callback = self.add
        else:
            self.callback = callback

    def __len__(self):
        return len(self.__inner)

    def __iter__(self):
        return iter(self.__inner)

    def __getitem__(self, key):
        if key in self.__inner:
            v = self.__inner[key]
            if len(v) == 1:
                return v[0]
            else:
                result = reduce(self.callback, v)
                self.__inner[key] = [result]
                return result
        raise KeyError

    def __contains__(self, key):
        return key in self.__inner

    def __setitem__(self, key, value):
        return self.__inner.__setitem__(key, [value])

    def __delitem__(self, key):
        return self.__inner.__delitem__(key)

    def __str__(self):
        return "MergeMap({0})".format(str(self.__inner))

    def __repr__(self):
        return str(self)

    def merge(self, *args, **kwargs):
        for each in args:
            for k, v in each.items():
                self.__inner[k].append(v)
        for k, v in kwargs.items():
            self.__inner[k].append(v)
        return self

    def add(self, a, b):
        return a + b

    def items(self):
        for k, v in self.__inner.items():
            if len(v) == 1:
                yield k, v[0]
            else:
                result = reduce(self.callback, v)
                self.__inner[k] = [result]
                yield k, result
