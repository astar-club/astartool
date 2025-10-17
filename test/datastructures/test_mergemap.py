from unittest import TestCase
from astartool.data_structure.mergemap import MergeMap
from astartool.error.lazydict_error import CircularReferenceError, ConstantRedefinitionError


class TestMergeDictionary(TestCase):

    def test_add(self):
        d = MergeMap()
        da = {"a": 1, "b": 2}
        db = {"b": 3, "c": 4}

        d.merge(da)
        d.merge(db)
        print(d)
        self.assertEqual(d["a"], 1)
        self.assertEqual(d["b"], 5)
        self.assertEqual(d["c"], 4)

    def test_append(self):
        d2 = MergeMap()
        da = {"a": [1], "b": [2]}
        db = {"b": [3], "c": [4]}
        d2.merge(da)
        d2.merge(db)
        self.assertListEqual(d2["a"], [1])
        self.assertListEqual(d2["b"], [2, 3])
        self.assertListEqual(d2["c"], [4])

    def test_set(self):
        add = lambda a, b: a | b

        d2 = MergeMap(callback=add)
        da = {"a": {1}, "b": {2}}
        db = {"b": {3}, "c": {4}}
        d2.merge(da)
        d2.merge(db)
        self.assertSetEqual(d2["a"], {1})
        self.assertSetEqual(d2["b"], {2, 3})
        self.assertSetEqual(d2["c"], {4})


