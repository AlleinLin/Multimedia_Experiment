import sys
'''
 把编码位置设置到输入数据流的开始位置。 
 查找窗口中最长的匹配串。 
 以“(Pointer, Length) Character”的格式输出，其中Pointer是指向窗口中匹配串的指针，Length表示匹配字符的长度，Character是前向缓冲存储器中的不匹配的第1个字符。 
 如果前向缓冲存储器不是空的，则把编码位置和窗口向前移(Length+1)个字符，然后返回到步骤2。
'''
def encode_lz77(text: str, window_size: int = 20, lookahead_buffer_size: int = 15) -> list[tuple[int, int, str]]:
    """
    使用LZ77算法对文本进行编码。
    LZ77算法基于滑动窗口和前向缓冲区来查找重复模式。
    它将文本分解为(偏移量, 长度, 下一个字符)三元组。
    Args:
        text (str): 要编码的原始文本字符串。
        window_size (int, optional): 滑动窗口的大小。定义了算法可以在多大范围内查找匹配,默认为20。
        lookahead_buffer_size (int, optional): 前向缓冲区的大小。定义了算法可以查看未来多远来找到最长匹配,默认为15。

    Returns:
        list[tuple[int, int, str]]: 编码后的数据列表。每个元素是一个三元组：
                                     - offset (int): 匹配的起始位置相对于当前编码位置的距离（回溯距离）。如果为0，表示没有匹配（或匹配长度为0）。
                                     - length (int): 匹配的长度。如果为0，表示没有匹配。
                                     - next_char (str): 匹配后紧随的第一个字符。如果匹配达到文本末尾，则为空字符串。如果offset和length都为0，则此为当前未匹配的字符。
    """
    encoded_output = []  # 存储编码后的三元组 (offset, length, next_char)
    current_position = 0  # 当前编码位置

    while current_position < len(text):
        best_match_length = 0
        best_match_offset = 0  # 存储偏移量，相对于当前位置的回溯距离

        # 定义当前窗口和前向缓冲区的范围
        window_start = max(0, current_position - window_size)
        lookahead_end = min(len(text), current_position + lookahead_buffer_size)

        # 当前前向缓冲区的内容
        lookahead_buffer = text[current_position:lookahead_end]

        if not lookahead_buffer:
            # 没有前向缓冲区，则当作没有匹配，直接输出当前字符
            next_char = text[current_position]
            encoded_output.append((0, 0, next_char))
            current_position += 1
            continue

        # 遍历窗口，查找最长匹配
        for i in range(window_start, current_position):
            for j in range(1, min(len(lookahead_buffer) + 1, current_position - i + 1)):
                if text[i: i + j] == lookahead_buffer[0: j]:
                    if j > best_match_length:
                        best_match_length = j
                        best_match_offset = current_position - i

        # 确定输出的三元组
        if best_match_length > 0:
            next_char_index = current_position + best_match_length
            next_char = text[next_char_index] if next_char_index < len(text) else ''

            encoded_output.append((best_match_offset, best_match_length, next_char))
            current_position += best_match_length + 1
        else:
            next_char = text[current_position]
            encoded_output.append((0, 0, next_char))
            current_position += 1

    return encoded_output

def decode_lz77(encoded_output: list[tuple[int, int, str]]) -> str:
    """
    使用LZ77算法解码编码后的数据。
    Args:
        encoded_output (list[tuple[int, int, str]]): 编码后的数据列表，每个元素是(偏移量, 长度, 下一个字符)三元组。
    Returns:
        str: 解码后的原始文本字符串。
    """
    decoded_string_parts = []

    for offset, length, next_char in encoded_output:
        # 处理匹配部分
        if length > 0:
            start_index_in_decoded = len(decoded_string_parts) - offset

            # 确保偏移量不超出范围
            for i in range(length):
                if start_index_in_decoded + i >= 0:
                    decoded_string_parts.append(decoded_string_parts[start_index_in_decoded + i])

        # 添加下一个字符
        if next_char:
            decoded_string_parts.append(next_char)

    return "".join(decoded_string_parts)


if __name__ == "__main__":
    if (len(sys.argv) != 2):
        exit("Usage: (Run with python lz77.py abracadabra)")

    stringToEncode = ' '.join(sys.argv[1:2])

    WINDOW_SIZE = 10
    LOOKAHEAD_BUFFER_SIZE = 5

    encoded_data = encode_lz77(stringToEncode, WINDOW_SIZE, LOOKAHEAD_BUFFER_SIZE)

    print("Encoded string (LZ77 - Offset, Length, Next Char):")
    for item in encoded_data:
        print("<{0}, {1}, {2}>".format(item[0], item[1], repr(item[2])), end=" ")
    print('\n')

    decoded_string = decode_lz77(encoded_data)

    print("Decoded string: ", end="")
    print(decoded_string)

