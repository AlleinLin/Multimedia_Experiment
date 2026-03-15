import unittest
from lz77 import encode_lz77, decode_lz77


class TestLZ77(unittest.TestCase):

    def test_basic_encoding_decoding(self):
        original_text = "abracadabra"
        self._run_test(original_text)

    def test_empty_string(self):
        original_text = ""
        self._run_test(original_text)

    def test_single_character(self):
        original_text = "a"
        self._run_test(original_text)

    def test_repeated_characters(self):
        original_text = "aaaaaa"
        self._run_test(original_text)

    def test_no_repeats(self):
        original_text = "abcdef"
        self._run_test(original_text)

    def test_edge_case_window_size(self):
        original_text = "abracadabra"
        encoded = encode_lz77(original_text, window_size=0)
        decoded = decode_lz77(encoded)
        self._print_result(original_text, decoded)

    def test_edge_case_lookahead_buffer_size(self):
        original_text = "abracadabra"
        encoded = encode_lz77(original_text, lookahead_buffer_size=0)
        decoded = decode_lz77(encoded)
        self._print_result(original_text, decoded)

    def test_large_input(self):
        original_text = "a" * 1000
        self._run_test(original_text)

    def test_special_characters(self):
        original_text = "a@b#c$d%e^f&g*h(i)j"
        self._run_test(original_text)

    def test_mixed_characters(self):
        original_text = "abcabcabc"
        self._run_test(original_text)

    def _run_test(self, original_text):
        encoded = encode_lz77(original_text)
        decoded = decode_lz77(encoded)
        self._print_result(original_text, decoded)

    def _print_result(self, original_text, decoded):
        result = "PASS" if original_text == decoded else "FAIL"
        print(f"Original: {original_text} | Decoded: {decoded} | Result: {result}")


if __name__ == '__main__':
    unittest.main()
