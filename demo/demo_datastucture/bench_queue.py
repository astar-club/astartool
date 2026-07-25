"""
LinkedQueue 性能基准测试

对比:
1. deque 纯数据结构   — append + popleft
2. LinkedList 纯数据结构 — append + pop(0)
3. queue.Queue (deque 后端, 带锁)
4. LinkedQueue  (LinkedList 后端, 带锁)
5. 内存占用
"""
import sys
import os
import timeit

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from collections import deque
from queue import Queue
from astartool.data_structure.linked_list import LinkedList
from astartool.data_structure.queue import LinkedQueue


def _run_all():
    # ---- 1. 纯数据结构 ----
    sizes = [100, 500, 1000, 5000, 10000]
    rounds = 500

    print("=" * 80)
    print("LinkedQueue 性能基准")
    print("=" * 80)
    print("\n--- 第1部分: 纯数据结构 append + pop(0)/popleft (无锁) ---")

    for n in sizes:
        t_d = min(timeit.repeat(
            f"for i in range({n}): dq.append(i)\nfor i in range({n}): dq.popleft()",
            "from collections import deque; dq = deque()",
            number=rounds, repeat=3))
        t_l = min(timeit.repeat(
            f"for i in range({n}): ll.append(i)\nfor i in range({n}): ll.pop(0)",
            "from astartool.data_structure.linked_list import LinkedList; ll = LinkedList()",
            number=rounds, repeat=3))
        print(f"  N={n:>6} | deque={t_d*1e6/n:7.1f}us | LinkedList={t_l*1e6/n:7.1f}us | "
              f"慢 {t_l/t_d:.1f}x")

    # ---- 2. 分别测 append / pop ----
    print("\n--- 第2部分: append vs pop(0) 单独耗时 ---")
    N_rep = 200

    for n in [1000, 5000, 10000]:
        t_da = min(timeit.repeat(
            f"dq.clear()\nfor i in range({n}): dq.append(i)",
            "from collections import deque; dq = deque()",
            number=N_rep, repeat=3))
        t_la = min(timeit.repeat(
            f"ll.clear()\nfor i in range({n}): ll.append(i)",
            "from astartool.data_structure.linked_list import LinkedList; ll = LinkedList()",
            number=N_rep, repeat=3))

        stmt_pop = f"for _ in range({N_rep}):\n dq = deque(range({n}))\n for i in range({n}): dq.popleft()"
        t_dp = min(timeit.repeat(stmt_pop, "from collections import deque", number=1, repeat=3))
        stmt_pop = f"for _ in range({N_rep}):\n ll = LinkedList(range({n}))\n for i in range({n}): ll.pop(0)"
        t_lp = min(timeit.repeat(stmt_pop,
                                 "from astartool.data_structure.linked_list import LinkedList",
                                 number=1, repeat=3))

        da = t_da * 1e6 / n
        dp = t_dp * 1e6 / (n * N_rep)
        la = t_la * 1e6 / n
        lp = t_lp * 1e6 / (n * N_rep)

        print(f"  N={n:>6}")
        print(f"    deque:      append={da:6.1f}us  popleft={dp:6.1f}us  合计={da+dp:6.1f}us")
        print(f"    LinkedList: append={la:6.1f}us  pop(0)={lp:6.1f}us  合计={la+lp:6.1f}us")
        print(f"    比值:       append={la/da:.1f}x       pop(0)={lp/dp:.1f}x       合计={(la+lp)/(da+dp):.1f}x")

    # ---- 3. Queue 级别 ----
    print("\n--- 第3部分: Queue 级别 (带 mutex 锁) ---")
    rounds = 500

    for n in [100, 500, 1000]:
        stmt = f"for i in range({n}): q.put(i)\nfor i in range({n}): q.get()"
        t_sys = min(timeit.repeat(stmt, "from queue import Queue; q = Queue()",
                                  number=rounds, repeat=3))
        t_lq = min(timeit.repeat(stmt,
                                 "from astartool.data_structure.queue import LinkedQueue; q = LinkedQueue()",
                                 number=rounds, repeat=3))
        print(f"  N={n:>6} | Queue={t_sys*1e6/n:7.1f}us | LinkedQueue={t_lq*1e6/n:7.1f}us | "
              f"慢 {t_lq/t_sys:.1f}x")

    # ---- 4. 大吞吐量 ----
    N = 100000
    rounds = 10
    print(f"\n--- 第4部分: 大吞吐量 {N:,} 次 put+get ---")

    S = f"for i in range({N}): dq.append(i)\nfor i in range({N}): dq.popleft()"
    t_d = min(timeit.repeat(S, "from collections import deque; dq = deque()", number=rounds, repeat=3))
    S = f"for i in range({N}): ll.append(i)\nfor i in range({N}): ll.pop(0)"
    t_l = min(timeit.repeat(S,
                            "from astartool.data_structure.linked_list import LinkedList; ll = LinkedList()",
                            number=rounds, repeat=3))
    S = f"for i in range({N}): q.put(i)\nfor i in range({N}): q.get()"
    t_q = min(timeit.repeat(S, "from queue import Queue; q = Queue()", number=rounds, repeat=3))
    t_lq = min(timeit.repeat(S,
                             "from astartool.data_structure.queue import LinkedQueue; q = LinkedQueue()",
                             number=rounds, repeat=3))

    print(f"  deque (纯):            {t_d*1000/rounds:8.2f} ms")
    print(f"  LinkedList (纯):       {t_l*1000/rounds:8.2f} ms  ({t_l/t_d:.1f}x)")
    print(f"  Queue (系统, 带锁):    {t_q*1000/rounds:8.2f} ms  (锁开销 {t_q/t_d:.1f}x)")
    print(f"  LinkedQueue (链表,带锁):{t_lq*1000/rounds:8.2f} ms  ({t_lq/t_q:.1f}x vs Queue)")

    # ---- 5. 内存 ----
    print("\n--- 第5部分: 内存占用 ---")
    try:
        import tracemalloc
        N_M = 20000
        tracemalloc.start()

        s1 = tracemalloc.take_snapshot()
        dq = deque()
        for i in range(N_M):
            dq.append(i)
        s2 = tracemalloc.take_snapshot()
        dq = None

        s3 = tracemalloc.take_snapshot()
        ll = LinkedList()
        for i in range(N_M):
            ll.append(i)
        s4 = tracemalloc.take_snapshot()

        total_d = sum(s.size_diff for s in s2.compare_to(s1, 'filename') if s.size_diff > 0)
        total_l = sum(s.size_diff for s in s4.compare_to(s3, 'filename') if s.size_diff > 0)

        print(f"  deque ({N_M} ints):       {total_d/1024:,.0f} KiB  ({total_d/N_M:.0f} B/node)")
        print(f"  LinkedList ({N_M} ints):  {total_l/1024:,.0f} KiB  ({total_l/N_M:.0f} B/node)")
        if total_d > 0:
            print(f"  内存比值: {total_l/total_d:.1f}x")
        tracemalloc.stop()
    except Exception:
        print("  (tracemalloc 不可用)")

    print("\n结论: LinkedList 纯操作慢 ~10x, 但 Queue 层锁开销 30x+ 稀释了差异到 1.5x。")


if __name__ == "__main__":
    _run_all()
