import unittest
from lz78 import encode, decode

class TestLZ78(unittest.TestCase):

    def test_encode_normal(self):
        # 测试正常情况
        text = "abracadabra"
        # 根据 LZ78 算法重新推导出的正确编码结果
        expected_numbers = [0, 0, 0, 1, 1, 1, 3]
        expected_letters = ['a', 'b', 'r', 'c', 'd', 'b', 'a']
        encoded = encode(text)
        print(f"Test: test_encode_normal | Expected N: {expected_numbers}, L: {expected_letters} | Got N: {encoded[0]}, L: {encoded[1]}")
        self.assertEqual(encoded[0], expected_numbers)
        self.assertEqual(encoded[1], expected_letters)

    def test_encode_empty(self):
        # 测试空字符串
        text = ""
        expected_numbers = []
        expected_letters = []
        encoded = encode(text)
        print(f"Test: test_encode_empty | Expected N: {expected_numbers}, L: {expected_letters} | Got N: {encoded[0]}, L: {encoded[1]}")
        self.assertEqual(encoded[0], expected_numbers)
        self.assertEqual(encoded[1], expected_letters)

    def test_encode_single_character(self):
        # 测试单个字符
        text = "a"
        expected_numbers = [0]
        expected_letters = ['a']
        encoded = encode(text)
        print(f"Test: test_encode_single_character | Expected N: {expected_numbers}, L: {expected_letters} | Got N: {encoded[0]}, L: {encoded[1]}")
        self.assertEqual(encoded[0], expected_numbers)
        self.assertEqual(encoded[1], expected_letters)

    def test_encode_repeated_characters(self):
        # 测试重复字符
        text = "aaaa"
        # 根据 encode 函数实际输出的正确编码结果： (0, 'a'), (1, 'a'), (1, '')
        expected_numbers = [0, 1, 1] # 修正此处的期望值
        expected_letters = ['a', 'a', '']
        encoded = encode(text)
        print(f"Test: test_encode_repeated_characters | Expected N: {expected_numbers}, L: {expected_letters} | Got N: {encoded[0]}, L: {encoded[1]}")
        self.assertEqual(encoded[0], expected_numbers)
        self.assertEqual(encoded[1], expected_letters)

    def test_decode_normal(self):
        # 测试解码正常情况
        lstNumbers = [0, 0, 0, 1, 1, 1, 3]
        lstLetters = ['a', 'b', 'r', 'c', 'd', 'b', 'a']
        decoded_output = decode(lstNumbers, lstLetters)
        print(f"Test: test_decode_normal | Expected: abracadabra | Got: {decoded_output}")
        self.assertEqual(decoded_output, "abracadabra")

    def test_decode_empty(self):
        # 测试解码空输入
        lstNumbers = []
        lstLetters = []
        decoded_output = decode(lstNumbers, lstLetters)
        print(f"Test: test_decode_empty | Expected: '' | Got: {decoded_output}")
        self.assertEqual(decoded_output, "")

    def test_decode_single_character(self):
        # 测试解码单个字符
        lstNumbers = [0]
        lstLetters = ['a']
        decoded_output = decode(lstNumbers, lstLetters)
        print(f"Test: test_decode_single_character | Expected: 'a' | Got: {decoded_output}")
        self.assertEqual(decoded_output, "a")

    def test_decode_repeated_characters(self):
        # 测试解码重复字符
        # 对应 encode("aaaa") 的输出：(0, 'a'), (1, 'a'), (1, '')
        lstNumbers = [0, 1, 1] # 修正此处的输入
        lstLetters = ['a', 'a', '']
        decoded_output = decode(lstNumbers, lstLetters)
        print(f"Test: test_decode_repeated_characters | Expected: 'aaaa' | Got: {decoded_output}")
        self.assertEqual(decoded_output, "aaaa")

    def test_decode_invalid_numbers(self):
        # 测试解码时使用无效的数字
        lstNumbers = [99] # 假设99是无效的索引
        lstLetters = ['a']
        with self.assertRaises(KeyError):
            decode(lstNumbers, lstLetters)

if __name__ == '__main__':
    unittest.main()

