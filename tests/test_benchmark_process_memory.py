import unittest

from scripts.benchmark_process_memory import normalize_maxrss, touch_memory


class ProcessMemoryBenchmarkTests(unittest.TestCase):
    def test_linux_maxrss_is_kib(self):
        self.assertEqual(normalize_maxrss(123, "Linux"), 123 * 1024)

    def test_darwin_maxrss_is_bytes(self):
        self.assertEqual(normalize_maxrss(123, "Darwin"), 123)

    def test_unknown_platform_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "unsupported"):
            normalize_maxrss(123, "Windows")

    def test_invalid_maxrss_fails_closed(self):
        for value in (-1, True, "123"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    normalize_maxrss(value, "Linux")

    def test_touch_memory_requires_positive_integer(self):
        for value in (0, -1, True):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    touch_memory(value)

    def test_touch_memory_is_deterministic(self):
        self.assertEqual(touch_memory(1), touch_memory(1))


if __name__ == "__main__":
    unittest.main()
