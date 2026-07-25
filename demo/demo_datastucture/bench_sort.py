"""
LinkedList.sort 性能基准测试

对比:
1. list.sort()       — 纯 C, 就地排序
2. sorted(list)      — 返回新 list
3. sorted(LinkedList)— 通过 __iter__ 提取后排序, 返回 list
4. LinkedList.sort() — 合并栈归并排序, O(log n) 额外空间, 就地修改
"""
import sys
import os
import timeit

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from astartool.data_structure.linked_list import LinkedList


def _run_all():
    sizes = [100, 500, 1000, 5000, 10000]
    rounds = 200

    print("=" * 80)
    print("LinkedList.sort 性能基准")
    print("=" * 80)

    for n in sizes:
        # 1. list.sort — 就地排序
        t_ls = min(timeit.repeat(
            f"data = list(range({n})); data.sort()",
            number=rounds, repeat=3))

        # 2. sorted(list)
        t_sl = min(timeit.repeat(
            f"data = list(range({n})); _ = sorted(data)",
            number=rounds, repeat=3))

        # 3. sorted(LinkedList)
        t_sll = min(timeit.repeat(
            f"ll = LinkedList(range({n})); _ = sorted(ll)",
            setup="from astartool.data_structure.linked_list import LinkedList",
            number=rounds, repeat=3))

        # 4. LinkedList.sort — 就地归并排序
        t_lls = min(timeit.repeat(
            f"ll = LinkedList(range({n})); ll.sort()",
            setup="from astartool.data_structure.linked_list import LinkedList",
            number=rounds, repeat=3))

        # 5. LinkedList.sort 纯排序开销 (扣除构造链表)
        t_lls_net = t_lls - (t_sll - t_sl)

        print(f"\n  N={n:>6}")
        print(f"    list.sort():          {t_ls*1e6/n:7.1f} us/op  (基准)")
        print(f"    sorted(list):         {t_sl*1e6/n:7.1f} us/op  ({t_sl/t_ls:.1f}x)")
        print(f"    sorted(LinkedList):   {t_sll*1e6/n:7.1f} us/op  ({t_sll/t_ls:.1f}x)")
        print(f"    LinkedList.sort():    {t_lls*1e6/n:7.1f} us/op  ({t_lls/t_ls:.1f}x)")
        print(f"    LL.sort 净排序(扣除构造): {t_lls_net*1e6/n:7.1f} us/op  ({t_lls_net/t_ls:.1f}x)")

    # 大吞吐量
    N = 100000
    rounds = 10
    print(f"\n{'=' * 80}")
    print(f"大吞吐量: {N:,} 元素, {rounds} rounds")
    print("=" * 80)

    t_ls = min(timeit.repeat(
        f"data = list(range({N})); data.sort()",
        number=rounds, repeat=3))
    t_sll = min(timeit.repeat(
        f"ll = LinkedList(range({N})); _ = sorted(ll)",
        setup="from astartool.data_structure.linked_list import LinkedList",
        number=rounds, repeat=3))
    t_lls = min(timeit.repeat(
        f"ll = LinkedList(range({N})); ll.sort()",
        setup="from astartool.data_structure.linked_list import LinkedList",
        number=rounds, repeat=3))

    print(f"  list.sort():          {t_ls*1000/rounds:8.2f} ms")
    print(f"  sorted(LinkedList):   {t_sll*1000/rounds:8.2f} ms  ({t_sll/t_ls:.1f}x)")
    print(f"  LinkedList.sort():    {t_lls*1000/rounds:8.2f} ms  ({t_lls/t_ls:.1f}x)")

    print("\n结论: LinkedList.sort 慢 10-20x, 根本原因是 Python 层面的指针跳转开销。")


if __name__ == "__main__":
    _run_all()
