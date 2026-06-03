# coding: utf-8

import heapq
from astartool.setuptool import PY310

if PY310:
    from collections.abc import MutableMapping
    from collections import defaultdict
else:
    from collections import MutableMapping, defaultdict


class RelationMap(MutableMapping):
    def __init__(self, relation_map=None, order=True, weight=False):
        self.__inner_dict = None
        self.order = order
        self.weight = weight
        if not self.order:
            self.__inner_dict = defaultdict(set)
        elif self.weight:
            self.__inner_dict = defaultdict(list)
        else:
            self.__inner_dict = defaultdict(list)

        if relation_map is not None:
            if isinstance(relation_map, dict):
                self.__inner_dict.update(relation_map)
            elif isinstance(relation_map, RelationMap):
                self.__inner_dict.update(relation_map.__inner_dict)
                self.order = relation_map.order
                self.weight = relation_map.weight

    def __getitem__(self, key, /):
        return self.__inner_dict.__getitem__(key)

    def __len__(self):
        return sum(map(len, self.__inner_dict.values()))

    def __iter__(self):
        data = list(self.__inner_dict.items())
        for k, li in data:
            for each in li:
                yield k, each

    def __setitem__(self, key, value):
        self.__inner_dict[key] = value

    def __eq__(self, other):
        return isinstance(other, RelationMap) and self.__inner_dict == other.__inner_dict

    def __delitem__(self, key):
        return self.__inner_dict.__delitem__(key)

    def pop(self, key, /):
        li = self.__inner_dict.pop(key)
        if len(li) == 1:
            return li.pop()
        else:
            if self.weight and self.order:
                res = heapq.heappop(li)
            else:
                res = li.pop()
            self.__inner_dict[key] = li
            return res

    def put(self, key, value, weight=None):
        if self.weight:
            if self.order:
                heapq.heappush(self.__inner_dict[key], (weight, value))
            else:
                self.__inner_dict[key].add((weight, value))
        else:
            if self.order:
                self.__inner_dict[key].append(value)
            else:
                self.__inner_dict[key].add(value)

    def reverse_map(self):
        result = RelationMap({}, order=self.order, weight=self.weight)
        if not self.weight:
            for k, li in self.__inner_dict.items():
                for each in li:
                    result.put(each, k)
        else:
            for k, li in self.__inner_dict.items():
                for each in li:
                    result.put(each[1], k, weight=each[0])
        return result

