import unittest

from astartool.number import gcd, is_prime


class TestNumber(unittest.TestCase):
    def test_gcd(self):
        assert gcd(151200, 362880) == 30240


class TestIsPrime(unittest.TestCase):
    def test_small_primes(self):
        for p in (2, 3, 5, 7, 11, 13, 17, 19, 23):
            self.assertTrue(is_prime(p))

    def test_small_composites(self):
        for c in (4, 6, 8, 9, 10, 12, 15, 21, 25):
            self.assertFalse(is_prime(c))

    def test_zero_and_one(self):
        # boundary values must return False (no exception)
        self.assertFalse(is_prime(0))
        self.assertFalse(is_prime(1))

    def test_large_prime(self):
        self.assertTrue(is_prime(7919))

    def test_uses_secrets_not_random(self):
        # guard against regression: is_prime must rely on secrets, not random
        import astartool.number._number as _m
        self.assertIn("secrets", _m.__dict__)
        # secrets.randbelow path should not raise for normal inputs
        self.assertTrue(is_prime(104729))

