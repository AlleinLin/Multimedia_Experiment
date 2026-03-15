import unittest
from lzw import encode, decode  # 假设你的 LZW 代码保存在 lzw.py 中


class TestLZW(unittest.TestCase):
    def _run_test_and_print(self, test_name, input_text):
        """Helper to run encode/decode and print inputs/outputs."""
        print(f"\n--- Running Test: {test_name} ---")
        print(f"Input: '{input_text}'")

        encoded, initial_dict_size = encode(input_text)
        print(f"Encoded (first 10 codes): {encoded[:10]}{'...' if len(encoded) > 10 else ''}")
        print(f"Encoded length: {len(encoded)}")

        decoded = decode(encoded)
        print(f"Decoded: '{decoded}'")

        self.assertEqual(decoded, input_text)
        return encoded, decoded

    def test_normal_input(self):
        """测试正常输入：普通字符串，包含重复模式"""
        input_text = "abracadabra"
        encoded, decoded = self._run_test_and_print("Normal Input", input_text)
        self.assertTrue(len(encoded) > 0)  # 确保编码输出不为空

    def test_empty_input(self):
        """测试边界值：空字符串"""
        input_text = ""
        encoded, decoded = self._run_test_and_print("Empty Input", input_text)
        self.assertEqual(encoded, [])  # 空输入应返回空码字列表

    def test_single_character(self):
        """测试边界值：单个字符"""
        input_text = "a"
        encoded, decoded = self._run_test_and_print("Single Character", input_text)
        self.assertEqual(len(encoded), 1)  # 单个字符编码后应只有一个码字

    def test_repetitive_string(self):
        """测试正常输入：高度重复的字符串，验证字典增长和压缩效果"""
        input_text = "aaaaaaa"
        encoded, decoded = self._run_test_and_print("Repetitive String", input_text)
        self.assertTrue(len(encoded) < len(input_text))  # 确保有压缩效果

    def test_no_repetition(self):
        """测试正常输入：无重复模式的字符串，验证编码后长度接近原文"""
        input_text = "abcdefg"
        encoded, decoded = self._run_test_and_print("No Repetition", input_text)
        # Note: LZW might sometimes result in slightly longer or equal length for very short, non-repetitive strings
        # due to code overhead, but for general cases, it's close.
        self.assertTrue(len(encoded) >= len(input_text) - 1)  # 无重复时编码长度接近原文

    def test_special_characters(self):
        """测试正常输入：包含特殊字符（ASCII 范围内）"""
        input_text = "!@#$%^&*()"
        encoded, decoded = self._run_test_and_print("Special Characters", input_text)

    def test_long_string(self):
        """测试边界值：长字符串，验证字典增长和性能"""
        input_text = "a" * 1000 + "b" * 1000  # 2000 个字符，包含重复模式
        encoded, decoded = self._run_test_and_print("Long String", input_text)
        self.assertTrue(len(encoded) < len(input_text))  # 确保有压缩效果

    def test_all_ascii(self):
        """测试边界值：包含所有初始字典中的 ASCII 字符"""
        input_text = "".join(chr(i) for i in range(256))
        encoded, decoded = self._run_test_and_print("All ASCII Characters", input_text)

    def test_invalid_code_in_decode(self):
        """测试异常值：解码时传入无效码字列表（手动构造）"""
        invalid_codes = [256, 257, 999999]  # 包含一个超出范围的码字
        print(f"\n--- Running Test: Invalid Code in Decode ---")
        print(f"Input codes: {invalid_codes}")
        with self.assertRaises(KeyError):  # 期望抛出 KeyError 或其他异常
            decode(invalid_codes)
        print("Expected KeyError caught successfully.")

    def test_mismatch_encode_decode(self):
        """测试异常值：编码和解码不匹配的情况（手动修改编码结果）"""
        input_text = "abracadabra"
        encoded, _ = encode(input_text)
        original_encoded_str = f"{encoded[:10]}{'...' if len(encoded) > 10 else ''}"

        # Make a copy to modify
        modified_encoded = list(encoded)

        # Ensure there's at least one code to modify
        if modified_encoded:
            modified_encoded[0] = 999999  # 手动修改编码结果为无效码字
        else:
            # For empty string, this test wouldn't make sense as there's no code to modify
            print("Skipping test_mismatch_encode_decode for empty encoded list.")
            return

        print(f"\n--- Running Test: Mismatch Encode/Decode (Modified Code) ---")
        print(f"Original Input: '{input_text}'")
        print(f"Original Encoded (first 10 codes): {original_encoded_str}")
        print(
            f"Modified Encoded (first code changed to 999999): {modified_encoded[:10]}{'...' if len(modified_encoded) > 10 else ''}")

        with self.assertRaises(KeyError):  # 期望抛出 KeyError
            decode(modified_encoded)
        print("Expected KeyError caught successfully after modifying encoded list.")


if __name__ == "__main__":
    unittest.main()
