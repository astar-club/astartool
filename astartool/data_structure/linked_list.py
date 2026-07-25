#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 深圳星河软通科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.astar.ltd
# @file: linked_list .py
# @time: 2020/5/21 17:24
# @Software: PyCharm
from typing import Union

from astartool.setuptool import PY310
if PY310:
    from collections.abc import Iterable, Sized
else:
    from collections import Iterable, Sized

from astartool.error import MethodNotFoundError, ParameterValueError


class DataNode(object):
    __slots__ = ('data', 'pre', 'next')

    def __init__(self, data=None, pre=None, next=None):
        self.data = data
        self.pre = pre
        self.next = next

    def __eq__(self, other):
        if isinstance(other, DataNode):
            return self.data == other.data
        else:
            return self.data == other

    def __str__(self):
        return str(self.data)


class LinkedList(Iterable, Sized):
    def __init__(self, seq: Iterable = (), flag=True):
        """

        :param seq:  初始化可迭代对象
        :param flag: 若可迭代对象是LinkedList, 那么flag=False, 否则此参数为True
        """
        self.__count = 0
        self.pre = self
        self.next = self
        if seq:
            self.extend(seq, flag=flag)

    def append(self, p_object, flag=True):
        """
        追加函数
        :param p_object:
        :param flag: p_object 是DataNode, 那么flag=False, 否则此参数为True
        :return:
        """
        if flag:
            p_object = DataNode(p_object, None, None)
        self.pre.next = p_object
        p_object.pre = self.pre
        self.pre = p_object
        p_object.next = self
        self.__count += 1

    def clear(self):  # real signature unknown; restored from __doc__
        """ L.clear() -> None -- remove all items from L """
        p = self.next
        while p is not None and p is not self:
            t = p.next
            p.pre = None
            p.next = None
            p = t
        self.pre = self.next = self
        self.__count = 0

    def copy(self):  # real signature unknown; restored from __doc__
        """ L.copy() -> list -- a shallow copy of L """
        return LinkedList(self, flag=True)

    def count(self, value):  # real signature unknown; restored from __doc__
        """ L.count(value) -> integer -- return number of occurrences of value """
        s = 0
        p = self.next
        while p is not self:
            if p.data == value:
                s += 1
            p = p.next
        return s

    def extend(self, iterable: Iterable, flag=True):
        """
        :param iterable:
        :param flag: 若可迭代对象不是LinkedList, 此参数True和False没有区别
        当flag=False时候，只修改指针，不会新创建DataNode对象.
        flag=True时候，会创建DataNode对象，显然flag=False更快，但是需要注意此方法需要慎用
        :return:
        """
        if flag:
            for each in iterable:
                self.append(each, flag)
        else:
            if not isinstance(iterable, LinkedList):
                for each in iterable:
                    self.append(each, flag=True)
                return
            self.pre.next = iterable.next
            iterable.next.pre = self.pre
            self.pre = iterable.pre
            iterable.pre.next = self
            self.__count += iterable.__count
            iterable.__count = 0
            iterable.next = iterable.pre = iterable
            del iterable

    def index(self, value, start=None, stop=None):  # real signature unknown; restored from __doc__
        """
        L.index(value, [start, [stop]]) -> integer -- return first index of value.
        Raises ValueError if the value is not present.
        """
        n = self.__count
        if n == 0:
            raise ValueError('value is not present')

        # 正规化 start
        s = start if start is not None else 0
        if s < 0:
            s += n
        if s < 0:
            s = 0

        # 正规化 stop
        e = stop if stop is not None else n
        if e < 0:
            e += n
        if e > n:
            e = n

        if s >= e:
            raise ValueError('value is not present')

        # 跳到起始位置
        p = self.next
        idx = 0
        while idx < s:
            p = p.next
            idx += 1

        # 在 [s, e) 范围内搜索
        while p is not self and idx < e:
            if p.data == value:
                return idx
            p = p.next
            idx += 1

        raise ValueError('value is not present')

    def insert(self, index, p_object, flag=True):
        """
        :param index:
        :param p_object:
        :param flag: 若是DataNode类型, 那么flag=False, 否则此参数为True
        :return:
        """
        # 空列表或插入尾部，直接 append
        if self.__count == 0 or index >= self.__count:
            self.append(p_object, flag=flag)
            return

        if index * 2 <= self.__count:
            # 靠近头部，从哨兵节点向后遍历
            p = self
            for _ in range(index):
                p = p.next
        else:
            # 靠近尾部，从尾结点向前遍历
            p = self.pre
            for _ in range(self.__count - index):
                p = p.pre
        if flag:
            p_object = DataNode(p_object)
        p_object.next = p.next
        p_object.pre = p
        p.next = p_object
        p_object.next.pre = p_object
        self.__count += 1

    def pop(self, index=-1):
        if abs(index) > self.__count or self.__count == 0:
            raise IndexError('index not found')

        half = self.__count // 2
        if index >= 0:
            # 正索引优化：靠近尾部时转为负索引反向遍历
            if index > half:
                index = index - self.__count
        else:
            # 负索引优化：靠近头部时转为正索引正向遍历
            if abs(index) > half:
                index = self.__count + index

        if index >= 0:
            p = self.next
            ind = 0
            while ind < index:
                p = p.next
                ind += 1
            p.pre.next = p.next
            p.next.pre = p.pre
            p.pre = None
            p.next = None
            self.__count -= 1
            return p.data
        else:
            p = self.pre
            ind = -1
            while ind > index:
                p = p.pre
                ind -= 1
            p.pre.next = p.next
            p.next.pre = p.pre
            p.pre = None
            p.next = None
            self.__count -= 1
            return p.data

    def remove(self, value):  # real signature unknown; restored from __doc__
        """
        L.remove(value) -> None -- remove first occurrence of value.
        Raises ValueError if the value is not present.
        """
        p = self.next
        while p is not None and p != self:
            if p.data == value:
                p.pre.next = p.next
                p.next.pre = p.pre
                p.pre = None
                p.next = None
                self.__count -= 1
                return
            p = p.next
        raise ValueError('the value is not present.')

    def reverse(self):  # real signature unknown; restored from __doc__
        """ L.reverse() -- reverse *IN PLACE* """
        p = self.next
        while p != self:
            p.next, p.pre = p.pre, p.next
            p = p.pre
        self.next, self.pre = self.pre, self.next

    def sort(self, key=None, reverse=False):
        """ L.sort(key=None, reverse=False) -> None -- stable sort *IN PLACE*
        合并栈归并排序，额外空间 O(log n) ≈ O(1) """
        n = self.__count
        if n <= 1:
            return

        # -- 从哨兵节点上卸下数据节点，变成线性链 --
        first = self.next
        last = self.pre
        first.pre = None
        last.next = None
        self.next = self.pre = self

        # -- 合并栈: 固定 32 个槽位，存 (head, size) --
        # 合并过程中不维护 pre 指针来减少开销，最后一次性修复
        STACK_SIZE = 32
        stack = [(None, 0)] * STACK_SIZE

        # -- 根据参数生成对应的内联归并函数，避免循环内函数调用 --
        def _make_merge():
            if key is None:
                if reverse:
                    def merge(ah, size_a, bh, size_b):
                        ca = cb = 0
                        # 初始化头节点
                        if ah.data >= bh.data:
                            head = tail = ah
                            ah = ah.next
                            ca = 1
                        else:
                            head = tail = bh
                            bh = bh.next
                            cb = 1
                        while ca < size_a and cb < size_b:
                            if ah.data >= bh.data:
                                tail.next = ah
                                tail = ah
                                ah = ah.next
                                ca += 1
                            else:
                                tail.next = bh
                                tail = bh
                                bh = bh.next
                                cb += 1
                        while ca < size_a:
                            tail.next = ah
                            tail = ah
                            ah = ah.next
                            ca += 1
                        while cb < size_b:
                            tail.next = bh
                            tail = bh
                            bh = bh.next
                            cb += 1
                        tail.next = None
                        return head, tail, size_a + size_b
                else:
                    def merge(ah, size_a, bh, size_b):
                        ca = cb = 0
                        if ah.data <= bh.data:
                            head = tail = ah
                            ah = ah.next
                            ca = 1
                        else:
                            head = tail = bh
                            bh = bh.next
                            cb = 1
                        while ca < size_a and cb < size_b:
                            if ah.data <= bh.data:
                                tail.next = ah
                                tail = ah
                                ah = ah.next
                                ca += 1
                            else:
                                tail.next = bh
                                tail = bh
                                bh = bh.next
                                cb += 1
                        while ca < size_a:
                            tail.next = ah
                            tail = ah
                            ah = ah.next
                            ca += 1
                        while cb < size_b:
                            tail.next = bh
                            tail = bh
                            bh = bh.next
                            cb += 1
                        tail.next = None
                        return head, tail, size_a + size_b
            else:
                if reverse:
                    def merge(ah, size_a, bh, size_b):
                        ca = cb = 0
                        if key(ah.data) >= key(bh.data):
                            head = tail = ah
                            ah = ah.next
                            ca = 1
                        else:
                            head = tail = bh
                            bh = bh.next
                            cb = 1
                        while ca < size_a and cb < size_b:
                            if key(ah.data) >= key(bh.data):
                                tail.next = ah
                                tail = ah
                                ah = ah.next
                                ca += 1
                            else:
                                tail.next = bh
                                tail = bh
                                bh = bh.next
                                cb += 1
                        while ca < size_a:
                            tail.next = ah
                            tail = ah
                            ah = ah.next
                            ca += 1
                        while cb < size_b:
                            tail.next = bh
                            tail = bh
                            bh = bh.next
                            cb += 1
                        tail.next = None
                        return head, tail, size_a + size_b
                else:
                    def merge(ah, size_a, bh, size_b):
                        ca = cb = 0
                        if key(ah.data) <= key(bh.data):
                            head = tail = ah
                            ah = ah.next
                            ca = 1
                        else:
                            head = tail = bh
                            bh = bh.next
                            cb = 1
                        while ca < size_a and cb < size_b:
                            if key(ah.data) <= key(bh.data):
                                tail.next = ah
                                tail = ah
                                ah = ah.next
                                ca += 1
                            else:
                                tail.next = bh
                                tail = bh
                                bh = bh.next
                                cb += 1
                        while ca < size_a:
                            tail.next = ah
                            tail = ah
                            ah = ah.next
                            ca += 1
                        while cb < size_b:
                            tail.next = bh
                            tail = bh
                            bh = bh.next
                            cb += 1
                        tail.next = None
                        return head, tail, size_a + size_b
            return merge

        merge_two = _make_merge()

        # -- 一趟扫描: 逐个取出节点作为 size=1 的 run 压栈并合并 --
        curr = first
        while curr is not None:
            next_node = curr.next
            curr.next = None  # 孤立当前节点
            run_h = run_t = curr
            run_sz = 1

            # 若栈顶存在相同大小的有序段，逐级合并
            level = 0
            while level < STACK_SIZE:
                sh, ss = stack[level]
                if ss == run_sz:
                    run_h, run_t, run_sz = merge_two(sh, ss, run_h, run_sz)
                    stack[level] = (None, 0)
                    level += 1
                else:
                    break
            stack[level] = (run_h, run_sz)
            curr = next_node

        # -- 合并栈上所有剩余有序段 --
        merged_h = merged_t = None
        merged_sz = 0
        for sh, ss in stack:
            if ss == 0:
                continue
            if merged_sz == 0:
                merged_h, merged_t, merged_sz = sh, sh, ss
            else:
                merged_h, merged_t, merged_sz = merge_two(
                    merged_h, merged_sz, sh, ss)

        # -- 一次性修复 pre 指针 --
        p = merged_h
        p.pre = None
        prev = None
        while p.next is not None:
            p.pre = prev
            prev = p
            p = p.next
        p.pre = prev
        merged_t = p

        # -- 重新挂回哨兵节点 --
        self.next = merged_h
        merged_h.pre = self
        self.pre = merged_t
        merged_t.next = self

    def print(self):
        p = self.next
        while p is not self:
            print(p.data, '->', end=' ')
            p = p.next
        print("END")

    def __add__(self, *args, **kwargs):  # real signature unknown
        """ Return self+value. """
        value = args[0]
        if isinstance(value, Sized):
            if len(value) != len(self):
                raise ValueError('error in input')
            c = LinkedList(map(lambda a, b: a + b, self, value))
            return c
        else:
            b = LinkedList(map(lambda a: a + value, self))
            return b

    def __eq__(self, *args, **kwargs):  # real signature unknown
        """ Return self==value. """
        value = args[0]
        if isinstance(value, LinkedList):
            if value is self:
                return True
        if isinstance(value, Sized) and len(value) == len(self):
            p = self.next
            for v in value:
                if p is self or p.data != v:
                    return False
                p = p.next
            return True
        return False

    def __getitem__(self, y):  # real signature unknown; restored from __doc__
        """ x.__getitem__(y) <==> x[y] """
        if isinstance(y, int):
            if y >= len(self) or y < -len(self):
                raise ParameterValueError("list out of range")

            half = len(self) // 2
            if y >= 0:
                # 正索引优化：靠近尾部时转为负索引反向遍历
                if y > half:
                    y = y - len(self)
            else:
                # 负索引优化：靠近头部时转为正索引正向遍历
                if abs(y) > half:
                    y = len(self) + y

            if y >= 0:
                p = self.next
                ind = 0
                while ind < y:
                    p = p.next
                    ind += 1

                return p.data
            else:
                p = self.pre
                ind = -1
                while ind > y:
                    p = p.pre
                    ind -= 1
                return p.data
        elif isinstance(y, slice):
            step = 1 if y.step is None else y.step
            if step == 0:
                raise ValueError("slice step cannot be zero")
            if step > 0:
                if y.start is None:
                    start = 0
                elif y.start < 0:
                    start = len(self) + y.start
                else:
                    start = y.start

                if y.stop is None:
                    stop = len(self)
                elif y.stop < 0:
                    stop = len(self) + y.stop
                else:
                    stop = y.stop
            else:
                if y.start is None:
                    start = len(self) - 1
                elif y.start < 0:
                    start = len(self) + y.start
                else:
                    start = y.start

                if y.stop is None:
                    stop = -1
                elif y.stop < 0:
                    stop = len(self) + y.stop
                else:
                    stop = y.stop
            cnt = self.__count
            if cnt == 0:
                return LinkedList()
            # 定位到起始节点
            if step > 0:
                if start >= cnt:
                    return LinkedList()
                p = self.next
                for _ in range(start):
                    p = p.next
            else:
                if start >= cnt:
                    start = cnt - 1
                p = self
                for _ in range(start + 1):
                    p = p.next
            li = LinkedList()
            i = start
            while (step > 0 and i < stop) or (step < 0 and i > stop):
                if p is self:
                    break
                li.append(p.data)
                if step > 0:
                    for _ in range(step):
                        p = p.next
                else:
                    for _ in range(-step):
                        p = p.pre
                i += step
            return li
        else:
            raise MethodNotFoundError('method not fount')

    #
    # def __ge__(self, *args, **kwargs):  # real signature unknown
    #     """ Return self>=value. """
    #     pass
    #
    # def __gt__(self, *args, **kwargs):  # real signature unknown
    #     """ Return self>value. """
    #     pass

    def __iadd__(self, *args, **kwargs):  # real signature unknown
        """ Implement self+=value. """
        value = args[0]
        if isinstance(value, Sized):
            if len(value) != len(self):
                raise ValueError('error in input')
            p = self.next
            for v in value:
                if p is self:
                    break
                p.data = p.data + v
                p = p.next
        else:
            p = self.next
            while p is not self:
                p.data = p.data + value
                p = p.next
        return self

    def __imul__(self, *args, **kwargs):  # real signature unknown
        """ Implement self*=value. """
        n = args[0]
        if not isinstance(n, int):
            raise TypeError("can't multiply sequence by non-int of type '{}'".format(type(n).__name__))
        if n <= 0:
            self.clear()
        elif n > 1:
            count = self.__count
            # 先快照原始数据
            original = [None] * count
            p = self.next
            i = 0
            while p is not self:
                original[i] = p.data
                p = p.next
                i += 1
            for _ in range(n - 1):
                for v in original:
                    self.append(v)
        return self

    def __len__(self, *args, **kwargs):  # real signature unknown
        """ Return len(self). """
        return self.__count

    def __le__(self, *args, **kwargs):  # real signature unknown
        """ Return self<=value. """
        raise MethodNotFoundError("method not found")

    def __lt__(self, *args, **kwargs):  # real signature unknown
        """ Return self<value. """
        raise MethodNotFoundError("method not found")

    def __mul__(self, *args, **kwargs):  # real signature unknown
        """ Return self*value. """
        n = args[0]
        if not isinstance(n, int):
            raise TypeError("can't multiply sequence by non-int of type '{}'".format(type(n).__name__))
        if n <= 0:
            return LinkedList()
        count = self.__count
        # 快照原始数据到 Python list（一次遍历）
        original = [None] * count
        p = self.next
        i = 0
        while p is not self:
            original[i] = p.data
            p = p.next
            i += 1
        result = LinkedList(original)
        for _ in range(n - 1):
            for v in original:
                result.append(v)
        return result

    def __iter__(self):
        p = self.next
        while p is not self:
            yield p.data
            p = p.next

    def __del__(self):
        # 逐个清理结点引用，断开循环引用以便GC正确回收
        p = self.next
        while p is not None and p is not self:
            t = p.next
            p.pre = None
            p.next = None
            p = t
        self.pre = None
        self.next = None


class Pointer:
    __slots__ = ('_Pointer__p',)

    def __init__(self, data_node: Union[DataNode, LinkedList]):
        self.__p = data_node

    def __add__(self, other):
        p = self
        if isinstance(other, int) and other > 0:
            for _ in range(other):
                if p.has_next():
                    p.next()
                else:
                    p.next()
                    break
            return p
        elif other < 0:
            return self - (-other)
        return p

    def __sub__(self, other):
        p = self
        if isinstance(other, int) and other > 0:
            for _ in range(other):
                if p.has_pre():
                    p.pre()
                else:
                    p.pre()
                    break
            return p
        elif other < 0:
            return self + (-other)
        return p

    def __iadd__(self, other):
        if isinstance(other, int):
            if other > 0:
                for _ in range(other):
                    if self.has_next():
                        self.next()
                    else:
                        self.next()
                        break
                return self
            elif other < 0:
                return self.__isub__(-other)
            return self
        raise ValueError("other must be int")

    def __isub__(self, other):
        if isinstance(other, int):
            if other > 0:
                for _ in range(other):
                    if self.has_pre():
                        self.pre()
                    else:
                        self.pre()
                        break
                return self
            elif other < 0:
                return self.__iadd__(-other)
            return self
        raise ValueError("other must be int")

    def has_next(self):
        return isinstance(self.__p.next, DataNode)

    def has_pre(self):
        return isinstance(self.__p.pre, DataNode)

    def is_last(self):
        return isinstance(self.__p, LinkedList)

    def next(self):
        self.__p = self.__p.next

    def pre(self):
        self.__p = self.__p.pre

    @property
    def data(self):
        try:
            return self.__p.data
        except AttributeError:
            raise ValueError('LinkedList has no data')

    @property
    def datanode(self):
        return self.__p
