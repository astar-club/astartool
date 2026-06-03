from unittest import TestCase
from astartool.data_structure.relation import RelationMap


class TestRelation(TestCase):

    def test_relation_map(self):
        d = RelationMap()
        d["1"] = ["2", "3"]
        d["2"] = ["3", "4"]
        d["3"] = ["4"]

        mmap = d.reverse_map()
        mmap2 = RelationMap({"2": ["1"], "3": ["1", "2"], "4": ["2", "3"]})
        self.assertEqual(mmap, mmap2)

    def test_relation_map_order(self):
        d = RelationMap(order=False)
        d["1"] = {"2", "3", "4"}
        d["2"] = {"3", "4"}
        d["3"] = {"4"}

        mmap = d.reverse_map()
        mmap2 = RelationMap({"2": {"1"}, "3": {"1", "2"}, "4": {"1", "2", "3"}})
        self.assertEqual(mmap, mmap2)

    def test_relation_map_order_weight(self):
        d = RelationMap(order=True, weight=True)
        d["1"] = [(1, "2"), (2,"3"), (4,"4")]
        d["2"] = [(1, "3"), (2, "4")]
        d["3"] = [(4, "4")]

        mmap = d.reverse_map()
        print(mmap._RelationMap__inner_dict.items())
        mmap2 = RelationMap({
                '2': [(1, '1')],
                '3': [(1, '2'), (2, '1')],
                '4': [(2, '2'), (4, '1'), (4, '3')]
            },
            order=True, weight=True)
        self.assertEqual(mmap, mmap2)

    def test_relation_map_weight(self):
        d = RelationMap(order=False, weight=True)
        d["1"] = {(1, "2"), (2, "3"), (4,"4")}
        d["2"] = {(1, "3"), (2, "4")}
        d["3"] = {(4, "4")}

        mmap = d.reverse_map()
        print(mmap._RelationMap__inner_dict.items())
        mmap2 = RelationMap({
                '2': {(1, '1')},
                '3': {(1, '2'), (2, '1')},
                '4': {(2, '2'), (4, '1'), (4, '3')}
            },
            order=False, weight=True)
        self.assertEqual(mmap, mmap2)