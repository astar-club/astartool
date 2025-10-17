# -*- coding: utf-8 -*-


from astartool.string import is_url, has_Chinese, is_email

from unittest import TestCase


class StringTestCase(TestCase):
    def test_is_url(self):
        url1 = "www.baidu.com"
        url2 = "www.snowland.ltd"
        url3 = "https://blog.csdn.net/"

        self.assertTrue(is_url(url1))
        self.assertTrue(is_url(url2))
        self.assertTrue(is_url(url3))

    def test_has_Chinese(self):
        text1 = "123"
        text2 = "A.Star陈~"
        self.assertFalse(has_Chinese(text1))
        self.assertTrue(has_Chinese(text2))

    def test_is_email(self):
        text1 = "astar@snowland.ltd"
        self.assertTrue(is_email(text1))
