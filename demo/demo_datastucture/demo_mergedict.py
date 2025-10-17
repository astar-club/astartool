from astartool.data_structure.mergemap import MergeMap


d = MergeMap()
da = {"a": 1, "b": 2}
db = {"b": 3, "c": 4}
d.merge(da)
d.merge(db)
for k, v in d.items():
    print("k:", k, "v:", v)



