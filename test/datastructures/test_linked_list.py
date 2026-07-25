from unittest import TestCase
from astartool.data_structure.linked_list import DataNode, LinkedList
from astartool.error import MethodNotFoundError, ParameterValueError


class TestDataNode(TestCase):

    def test_init(self):
        node = DataNode(1)
        self.assertEqual(node.data, 1)
        self.assertIsNone(node.pre)
        self.assertIsNone(node.next)

    def test_init_with_links(self):
        pre_node = DataNode(0)
        next_node = DataNode(2)
        node = DataNode(1, pre=pre_node, next=next_node)
        self.assertEqual(node.data, 1)
        self.assertIs(node.pre, pre_node)
        self.assertIs(node.next, next_node)

    def test_eq_data_node(self):
        a = DataNode(1)
        b = DataNode(1)
        c = DataNode(2)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_eq_raw_value(self):
        node = DataNode(1)
        self.assertEqual(node, 1)
        self.assertNotEqual(node, 2)

    def test_str(self):
        node = DataNode("hello")
        self.assertEqual(str(node), "hello")

    def test_del_unlinks_from_neighbors(self):
        """通过 LinkedList 的 remove 操作验证节点安全拔出"""
        li = LinkedList([0, 1, 2])
        li.remove(1)
        self.assertEqual(list(li), [0, 2])


class TestLinkedListInit(TestCase):

    def test_default_init(self):
        li = LinkedList()
        self.assertEqual(len(li), 0)

    def test_init_with_list(self):
        li = LinkedList([1, 2, 3])
        self.assertEqual(len(li), 3)
        self.assertEqual(list(li), [1, 2, 3])

    def test_init_with_tuple(self):
        li = LinkedList((1, 2, 3))
        self.assertEqual(len(li), 3)

    def test_init_bad_flag(self):
        """flag=False 但传入的不是 LinkedList，应回退为逐元素追加"""
        li = LinkedList([1, 2, 3], flag=False)
        self.assertEqual(len(li), 3)
        self.assertEqual(list(li), [1, 2, 3])


class TestLinkedListAppend(TestCase):

    def test_append(self):
        li = LinkedList()
        li.append(1)
        li.append(2)
        self.assertEqual(len(li), 2)
        self.assertEqual(list(li), [1, 2])

    def test_append_as_datanode(self):
        li = LinkedList()
        node = DataNode(99)
        li.append(node, flag=False)
        self.assertEqual(len(li), 1)
        self.assertEqual(list(li), [99])


class TestLinkedListClear(TestCase):

    def test_clear(self):
        li = LinkedList([1, 2, 3])
        li.clear()
        self.assertEqual(len(li), 0)
        self.assertEqual(list(li), [])

    def test_clear_empty(self):
        li = LinkedList()
        li.clear()
        self.assertEqual(len(li), 0)


class TestLinkedListCopy(TestCase):

    def test_copy(self):
        li = LinkedList([1, 2, 3])
        cp = li.copy()
        self.assertTrue(isinstance(cp, LinkedList))
        self.assertEqual(len(cp), 3)
        self.assertEqual(list(cp), [1, 2, 3])
        # 浅拷贝: 修改 cp 不影响原链表
        cp.append(4)
        self.assertEqual(len(li), 3)


class TestLinkedListCount(TestCase):

    def test_count(self):
        li = LinkedList([1, 2, 2, 3])
        self.assertEqual(li.count(2), 2)
        self.assertEqual(li.count(1), 1)
        self.assertEqual(li.count(99), 0)

    def test_count_empty(self):
        li = LinkedList()
        self.assertEqual(li.count(1), 0)


class TestLinkedListExtend(TestCase):

    def test_extend_list(self):
        li = LinkedList([1, 2])
        li.extend([3, 4])
        self.assertEqual(len(li), 4)
        self.assertEqual(list(li), [1, 2, 3, 4])

    def test_extend_empty(self):
        li = LinkedList()
        li.extend([1, 2, 3])
        self.assertEqual(len(li), 3)
        self.assertEqual(list(li), [1, 2, 3])

    def test_extend_linked_list_copy(self):
        a = LinkedList([1, 2])
        b = LinkedList([3, 4])
        a.extend(b, flag=True)
        self.assertEqual(len(a), 4)
        self.assertEqual(len(b), 2)

    def test_extend_linked_list_fast(self):
        """flag=False: 直接拼接指针，源链表被消耗"""
        a = LinkedList([1, 2])
        b = LinkedList([3, 4])
        a.extend(b, flag=False)
        self.assertEqual(len(a), 4)
        self.assertEqual(list(a), [1, 2, 3, 4])
        # b 应该已被清空
        self.assertEqual(len(b), 0)


class TestLinkedListIndex(TestCase):

    def test_index_found(self):
        li = LinkedList([1, 2, 3])
        self.assertEqual(li.index(2), 1)

    def test_index_first(self):
        li = LinkedList([1, 1, 1])
        self.assertEqual(li.index(1), 0)

    def test_index_not_found(self):
        li = LinkedList([1, 2, 3])
        with self.assertRaises(ValueError):
            li.index(99)

    # -- start / stop --

    def test_index_with_start(self):
        li = LinkedList([1, 2, 3, 2, 5])
        self.assertEqual(li.index(2, 2), 3)  # 从索引2开始找到第二个2

    def test_index_with_start_negative(self):
        li = LinkedList([1, 2, 3, 2, 5])
        self.assertEqual(li.index(2, -2), 3)  # 负数start: 从倒数第2个开始

    def test_index_with_start_and_stop(self):
        li = LinkedList([1, 2, 3, 2, 5])
        self.assertEqual(li.index(3, 1, 4), 2)

    def test_index_with_stop_exclusive(self):
        """stop 是排他的，不会搜到 stop 位置"""
        li = LinkedList([10, 20, 30, 40])
        with self.assertRaises(ValueError):
            li.index(30, 0, 2)  # 30 在索引2，不在 [0,2) 内

    def test_index_stop_negative(self):
        li = LinkedList([1, 2, 3, 4, 5])
        self.assertEqual(li.index(2, 0, -2), 1)

    def test_index_empty_range(self):
        """start >= stop 时直接抛异常"""
        li = LinkedList([1, 2, 3])
        with self.assertRaises(ValueError):
            li.index(1, 2, 2)
        with self.assertRaises(ValueError):
            li.index(1, 3, 1)

    def test_index_not_found_in_range(self):
        li = LinkedList([1, 2, 3, 2, 5])
        with self.assertRaises(ValueError):
            li.index(2, 0, 1)  # 2 不在 [0,1) 范围内


class TestLinkedListInsert(TestCase):

    def test_insert_beginning(self):
        li = LinkedList([2, 3])
        li.insert(0, 1)
        self.assertEqual(list(li), [1, 2, 3])

    def test_insert_middle(self):
        li = LinkedList([1, 3])
        li.insert(1, 2)
        self.assertEqual(list(li), [1, 2, 3])

    def test_insert_as_datanode(self):
        li = LinkedList([1, 3])
        node = DataNode(2)
        li.insert(1, node, flag=False)
        self.assertEqual(list(li), [1, 2, 3])

    def test_insert_end(self):
        li = LinkedList([1, 2])
        li.insert(2, 3)
        self.assertEqual(list(li), [1, 2, 3])

    def test_insert_empty(self):
        li = LinkedList()
        li.insert(0, 1)
        self.assertEqual(list(li), [1])


class TestLinkedListPop(TestCase):

    def test_pop_last(self):
        li = LinkedList([1, 2, 3])
        val = li.pop()
        self.assertEqual(val, 3)
        self.assertEqual(list(li), [1, 2])

    def test_pop_index(self):
        li = LinkedList([1, 2, 3])
        val = li.pop(0)
        self.assertEqual(val, 1)
        self.assertEqual(list(li), [2, 3])

    def test_pop_negative(self):
        li = LinkedList([1, 2, 3])
        val = li.pop(-2)
        self.assertEqual(val, 2)
        self.assertEqual(list(li), [1, 3])

    def test_pop_out_of_range(self):
        li = LinkedList([1, 2])
        with self.assertRaises(IndexError):
            li.pop(5)


class TestLinkedListRemove(TestCase):

    def test_remove_found(self):
        li = LinkedList([1, 2, 3])
        li.remove(2)
        self.assertEqual(list(li), [1, 3])

    def test_remove_first_occurrence(self):
        li = LinkedList([1, 2, 2, 3])
        li.remove(2)
        self.assertEqual(list(li), [1, 2, 3])

    def test_remove_not_found(self):
        li = LinkedList([1, 2, 3])
        with self.assertRaises(ValueError):
            li.remove(99)


class TestLinkedListReverse(TestCase):

    def test_reverse(self):
        li = LinkedList([1, 2, 3])
        li.reverse()
        self.assertEqual(list(li), [3, 2, 1])

    def test_reverse_single(self):
        li = LinkedList([1])
        li.reverse()
        self.assertEqual(list(li), [1])

    def test_reverse_empty(self):
        li = LinkedList()
        li.reverse()
        self.assertEqual(list(li), [])


class TestLinkedListSort(TestCase):

    def test_sort_basic(self):
        li = LinkedList([3, 1, 2])
        li.sort()
        self.assertEqual(list(li), [1, 2, 3])

    def test_sort_already_sorted(self):
        li = LinkedList([1, 2, 3])
        li.sort()
        self.assertEqual(list(li), [1, 2, 3])

    def test_sort_reverse(self):
        li = LinkedList([1, 2, 3])
        li.sort(reverse=True)
        self.assertEqual(list(li), [3, 2, 1])

    def test_sort_with_key(self):
        li = LinkedList([-3, 1, -2])
        li.sort(key=abs)
        self.assertEqual(list(li), [1, -2, -3])

    def test_sort_strings(self):
        li = LinkedList(["banana", "apple", "cherry"])
        li.sort()
        self.assertEqual(list(li), ["apple", "banana", "cherry"])

    def test_sort_empty(self):
        li = LinkedList()
        li.sort()
        self.assertEqual(list(li), [])

    def test_sort_single(self):
        li = LinkedList([42])
        li.sort()
        self.assertEqual(list(li), [42])

    def test_sort_duplicates(self):
        li = LinkedList([2, 1, 2, 1, 3])
        li.sort()
        self.assertEqual(list(li), [1, 1, 2, 2, 3])

    def test_sort_stable(self):
        """稳定排序: key 相同的元素保持原有相对顺序"""
        pairs = [(1, 'b'), (1, 'a'), (2, 'c'), (0, 'd')]
        li = LinkedList(pairs)
        li.sort(key=lambda x: x[0])
        self.assertEqual(list(li), [(0, 'd'), (1, 'b'), (1, 'a'), (2, 'c')])



class TestLinkedListGetItem(TestCase):

    def test_getitem_int(self):
        li = LinkedList([1, 2, 3])
        self.assertEqual(li[0], 1)
        self.assertEqual(li[2], 3)

    def test_getitem_negative(self):
        li = LinkedList([1, 2, 3])
        self.assertEqual(li[-1], 3)
        self.assertEqual(li[-2], 2)

    def test_getitem_out_of_range(self):
        li = LinkedList([1, 2])
        with self.assertRaises(ParameterValueError):
            _ = li[5]

    def test_getitem_slice_forward(self):
        li = LinkedList([1, 2, 3, 4, 5])
        sub = li[1:4]
        self.assertTrue(isinstance(sub, LinkedList))
        self.assertEqual(list(sub), [2, 3, 4])

    def test_getitem_slice_with_step(self):
        li = LinkedList([1, 2, 3, 4, 5])
        sub = li[::2]
        self.assertEqual(list(sub), [1, 3, 5])

    def test_getitem_slice_negative_step(self):
        li = LinkedList([1, 2, 3, 4, 5])
        sub = li[::-1]
        self.assertEqual(list(sub), [5, 4, 3, 2, 1])

    def test_getitem_slice_empty(self):
        li = LinkedList([1, 2, 3])
        sub = li[3:5]
        self.assertEqual(list(sub), [])


class TestLinkedListLen(TestCase):

    def test_len(self):
        li = LinkedList([1, 2, 3])
        self.assertEqual(len(li), 3)

    def test_len_empty(self):
        li = LinkedList()
        self.assertEqual(len(li), 0)

    def test_len_after_append(self):
        li = LinkedList()
        li.append(1)
        self.assertEqual(len(li), 1)

    def test_len_after_clear(self):
        li = LinkedList([1, 2, 3])
        li.clear()
        self.assertEqual(len(li), 0)


class TestLinkedListIteration(TestCase):

    def test_iter(self):
        li = LinkedList([1, 2, 3])
        result = []
        for x in li:
            result.append(x)
        self.assertEqual(result, [1, 2, 3])

    def test_list_conversion(self):
        li = LinkedList([1, 2, 3])
        self.assertEqual(list(li), [1, 2, 3])

    def test_iter_empty(self):
        li = LinkedList()
        self.assertEqual(list(li), [])


class TestLinkedListEq(TestCase):

    def test_eq_same_list(self):
        a = LinkedList([1, 2, 3])
        b = LinkedList([1, 2, 3])
        self.assertEqual(a, b)

    def test_eq_different(self):
        a = LinkedList([1, 2, 3])
        b = LinkedList([1, 2])
        self.assertNotEqual(a, b)

    def test_eq_python_list(self):
        a = LinkedList([1, 2, 3])
        self.assertEqual(a, [1, 2, 3])
        self.assertNotEqual(a, [1, 2])

    def test_eq_same_id(self):
        a = LinkedList([1, 2, 3])
        self.assertEqual(a, a)


class TestLinkedListAdd(TestCase):

    def test_add_elementwise(self):
        a = LinkedList([1, 2, 3])
        b = LinkedList([4, 5, 6])
        result = a + b
        self.assertTrue(isinstance(result, LinkedList))
        self.assertEqual(list(result), [5, 7, 9])

    def test_add_scalar(self):
        a = LinkedList([1, 2, 3])
        result = a + 1
        self.assertEqual(list(result), [2, 3, 4])

    def test_add_mismatched_length(self):
        a = LinkedList([1, 2])
        b = LinkedList([1, 2, 3])
        with self.assertRaises(ValueError):
            _ = a + b


class TestLinkedListIAdd(TestCase):

    def test_iadd_elementwise(self):
        a = LinkedList([1, 2, 3])
        b = LinkedList([4, 5, 6])
        a += b
        self.assertTrue(isinstance(a, LinkedList))
        self.assertEqual(list(a), [5, 7, 9])

    def test_iadd_scalar(self):
        a = LinkedList([1, 2, 3])
        a += 1
        self.assertEqual(list(a), [2, 3, 4])

    def test_iadd_mismatched_length(self):
        a = LinkedList([1, 2])
        b = LinkedList([1, 2, 3])
        with self.assertRaises(ValueError):
            a += b

    def test_iadd_empty(self):
        a = LinkedList()
        b = LinkedList()
        a += b
        self.assertEqual(list(a), [])

    def test_iadd_self(self):
        """原链表对象不变"""
        a = LinkedList([1, 2, 3])
        a_id = id(a)
        a += 1
        self.assertEqual(id(a), a_id)


class TestLinkedListIMul(TestCase):

    def test_imul_positive(self):
        a = LinkedList([1, 2])
        a *= 3
        self.assertEqual(list(a), [1, 2, 1, 2, 1, 2])
        self.assertEqual(len(a), 6)

    def test_imul_one(self):
        a = LinkedList([1, 2, 3])
        a *= 1
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(len(a), 3)

    def test_imul_zero(self):
        a = LinkedList([1, 2, 3])
        a *= 0
        self.assertEqual(list(a), [])
        self.assertEqual(len(a), 0)

    def test_imul_negative(self):
        a = LinkedList([1, 2, 3])
        a *= -1
        self.assertEqual(list(a), [])
        self.assertEqual(len(a), 0)

    def test_imul_empty(self):
        a = LinkedList()
        a *= 5
        self.assertEqual(list(a), [])
        self.assertEqual(len(a), 0)

    def test_imul_non_int(self):
        a = LinkedList([1, 2])
        with self.assertRaises(TypeError):
            a *= "hello"

    def test_imul_self(self):
        """原链表对象不变"""
        a = LinkedList([1, 2])
        a_id = id(a)
        a *= 3
        self.assertEqual(id(a), a_id)


class TestLinkedListMul(TestCase):

    def test_mul_positive(self):
        a = LinkedList([1, 2])
        result = a * 3
        self.assertTrue(isinstance(result, LinkedList))
        self.assertEqual(list(result), [1, 2, 1, 2, 1, 2])
        self.assertEqual(len(result), 6)
        # 原链表不变
        self.assertEqual(list(a), [1, 2])

    def test_mul_one(self):
        a = LinkedList([1, 2, 3])
        result = a * 1
        self.assertEqual(list(result), [1, 2, 3])
        self.assertEqual(len(result), 3)

    def test_mul_zero(self):
        a = LinkedList([1, 2, 3])
        result = a * 0
        self.assertTrue(isinstance(result, LinkedList))
        self.assertEqual(list(result), [])
        self.assertEqual(len(result), 0)

    def test_mul_negative(self):
        a = LinkedList([1, 2, 3])
        result = a * -1
        self.assertTrue(isinstance(result, LinkedList))
        self.assertEqual(list(result), [])
        self.assertEqual(len(result), 0)

    def test_mul_empty(self):
        a = LinkedList()
        result = a * 5
        self.assertEqual(list(result), [])
        self.assertEqual(len(result), 0)

    def test_mul_non_int(self):
        a = LinkedList([1, 2])
        with self.assertRaises(TypeError):
            _ = a * "hello"

    def test_mul_returns_new_object(self):
        """乘法返回新对象"""
        a = LinkedList([1, 2])
        result = a * 3
        self.assertIsNot(a, result)


class TestLinkedListEdgeCases(TestCase):

    def test_large_list(self):
        n = 1000
        li = LinkedList(range(n))
        self.assertEqual(len(li), n)
        self.assertEqual(li[0], 0)
        self.assertEqual(li[n - 1], n - 1)
        self.assertEqual(list(li), list(range(n)))

    def test_mixed_types(self):
        li = LinkedList([1, "hello", 3.14, None])
        self.assertEqual(list(li), [1, "hello", 3.14, None])

    def test_print_does_not_raise(self):
        li = LinkedList([1, 2, 3])
        # print 方法不应抛异常
        try:
            li.print()
        except Exception as e:
            self.fail(f"print() raised {type(e).__name__}: {e}")


class TestLinkedListUnhashable(TestCase):
    """不可哈希对象（list/dict/set）在 LinkedList 中的表现"""

    # -- 构造与基本存取 --

    def test_store_lists(self):
        li = LinkedList([[1, 2], [3, 4], [5, 6]])
        self.assertEqual(len(li), 3)
        self.assertEqual(li[0], [1, 2])
        self.assertEqual(list(li), [[1, 2], [3, 4], [5, 6]])

    def test_store_dicts(self):
        d1 = {"a": 1}
        d2 = {"b": 2}
        li = LinkedList([d1, d2])
        self.assertEqual(li[0], {"a": 1})
        self.assertEqual(li[1], {"b": 2})

    def test_store_sets(self):
        s1 = {1, 2}
        s2 = {3, 4}
        li = LinkedList([s1, s2])
        self.assertEqual(li[0], {1, 2})

    def test_store_mixed_unhashable(self):
        li = LinkedList([[1], {"k": "v"}, {9}])
        self.assertEqual(len(li), 3)

    # -- append / insert / pop --

    def test_append_unhashable(self):
        li = LinkedList()
        li.append([1, 2, 3])
        li.append({"x": 10})
        self.assertEqual(li[0], [1, 2, 3])
        self.assertEqual(li[1], {"x": 10})

    def test_insert_unhashable(self):
        li = LinkedList([[1], [3]])
        li.insert(1, [2])
        self.assertEqual(list(li), [[1], [2], [3]])

    def test_pop_unhashable(self):
        li = LinkedList([[1], [2], [3]])
        val = li.pop(1)
        self.assertEqual(val, [2])
        self.assertEqual(list(li), [[1], [3]])

    # -- remove --

    def test_remove_unhashable_found(self):
        target = [2, 3]
        li = LinkedList([[1, 2], target, [4, 5]])
        li.remove([2, 3])
        self.assertEqual(list(li), [[1, 2], [4, 5]])

    def test_remove_unhashable_not_found(self):
        li = LinkedList([[1], [2], [3]])
        with self.assertRaises(ValueError):
            li.remove([99])

    # -- index --

    def test_index_unhashable(self):
        li = LinkedList([[10], [20], [30]])
        self.assertEqual(li.index([20]), 1)

    def test_index_unhashable_not_found(self):
        li = LinkedList([[1], [2]])
        with self.assertRaises(ValueError):
            li.index([99])

    # -- count --

    def test_count_unhashable(self):
        li = LinkedList([[1, 2], [3, 4], [1, 2]])
        self.assertEqual(li.count([1, 2]), 2)

    # -- __eq__ --

    def test_eq_unhashable(self):
        a = LinkedList([[1, 2], [3, 4]])
        b = LinkedList([[1, 2], [3, 4]])
        self.assertEqual(a, b)

    def test_eq_unhashable_diff(self):
        a = LinkedList([[1, 2], [3, 4]])
        b = LinkedList([[1, 2], [9, 9]])
        self.assertNotEqual(a, b)

    def test_eq_with_python_list_of_unhashable(self):
        a = LinkedList([[1], [2]])
        self.assertEqual(a, [[1], [2]])

    # -- __add__ / __iadd__ --

    def test_add_unhashable_elementwise(self):
        """list + list 为拼接"""
        a = LinkedList([[1], [2]])
        b = LinkedList([[3], [4]])
        result = a + b
        self.assertEqual(list(result), [[1, 3], [2, 4]])

    def test_iadd_unhashable_elementwise(self):
        a = LinkedList([[1], [2]])
        b = LinkedList([[3], [4]])
        a += b
        self.assertEqual(list(a), [[1, 3], [2, 4]])

    # -- 迭代 --

    def test_iter_unhashable(self):
        li = LinkedList([[1], [2], [3]])
        result = [x for x in li]
        self.assertEqual(result, [[1], [2], [3]])

    # -- 切片 --

    def test_slice_unhashable(self):
        li = LinkedList([[1], [2], [3], [4]])
        sub = li[1:3]
        self.assertEqual(list(sub), [[2], [3]])

    # -- copy --

    def test_copy_unhashable(self):
        li = LinkedList([[1, 2], [3, 4]])
        cp = li.copy()
        self.assertEqual(list(cp), [[1, 2], [3, 4]])
        # 浅拷贝：内部列表是同一个对象
        self.assertIs(li[0], cp[0])

    # -- reverse --

    def test_reverse_unhashable(self):
        li = LinkedList([[1], [2], [3]])
        li.reverse()
        self.assertEqual(list(li), [[3], [2], [1]])

    # -- clear --

    def test_clear_unhashable(self):
        li = LinkedList([[1], {"a": 1}, {2}])
        li.clear()
        self.assertEqual(len(li), 0)

    # -- 空列表操作 --

    def test_empty_unhashable_remove(self):
        li = LinkedList()
        with self.assertRaises(ValueError):
            li.remove([1])

    def test_empty_unhashable_index(self):
        li = LinkedList()
        with self.assertRaises(ValueError):
            li.index([1])

    def test_empty_unhashable_count(self):
        li = LinkedList()
        self.assertEqual(li.count([1]), 0)
