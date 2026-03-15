import sys

# LZW 初始字典大小，通常是 256（对应扩展 ASCII 或字节值）
# 新的字符/序列会动态添加到字典中。
INITIAL_DICT_SIZE = 256

def encode(text):
    """
    使用 LZW 算法对输入文本进行编码。
    Args:
        text (str): 需要编码的输入文本。
    Returns:
        tuple: (编码后的码字序列, 最终字典)。
    """
    # 1. 初始化字典
    dictionary = {chr(i): i for i in range(INITIAL_DICT_SIZE)}
    next_code = INITIAL_DICT_SIZE

    output_codes = []  # 存储编码后的码字序列

    if not text:
        return output_codes, dictionary  # 空字符串返回空码字列表和初始字典

    current_sequence = text[0]  # 初始化当前序列为文本的第一个字符

    # 2. 遍历输入文本
    for char in text[1:]:
        new_sequence = current_sequence + char
        if new_sequence in dictionary:
            current_sequence = new_sequence
        else:
            output_codes.append(dictionary[current_sequence])
            dictionary[new_sequence] = next_code
            next_code += 1
            current_sequence = char

    # 3. 循环结束后，输出最后一个当前序列的码字
    output_codes.append(dictionary[current_sequence])

    return output_codes, dictionary

def decode(output_codes):
    """
    使用 LZW 算法对码字序列进行解码。
    此实现遵循标准 LZW 解码逻辑：边解码边重建字典。
    Args:
        output_codes (list): 编码后的码字序列。
    Returns:
        str: 解码后的字符串。
    """
    # 1. 初始化字典 (与编码器相同)
    # 字典将码字映射回字符/字符串,所有可能的字符加入词典，当前前缀P是空的
    dictionary = {i: chr(i) for i in range(INITIAL_DICT_SIZE)}
    next_code = INITIAL_DICT_SIZE

    if not output_codes:
        return "" # 空码字列表返回空字符串

    # 2. 初始化第一个解码字符串
    # 第一个码字一定对应一个初始字典中的字符 当前字符(C) =字符流中的下一个字符
    decoded_string = dictionary[output_codes[0]]
    previous_sequence = decoded_string[0] # previous_sequence 是上一个解码出来的字符串
    '''
    判断前缀=字符串P+C是否在词典中
    如果“是”：P = P+C ；
    如果“否”
    ① 把代表当前前缀P的码字输出到码字流;
    ② 把前缀-字符串P+C添加到词典;
    ③ 令当前前缀P = C ;

    '''
    # 3. 遍历码字序列 (从第二个码字开始)
    for code in output_codes[1:]:
        current_sequence = ""
        if code in dictionary:
            # 如果当前码字在字典中，直接获取其对应的字符串
            current_sequence = dictionary[code]
        else:
            # 如果当前码字不在字典中，这是 LZW 解码的特殊情况：
            # k = S + S[0]，其中 S 是前一个解码出的字符串。
            # 编码器在输出 "XXX" 后，下一轮遇到 "XXXX"，会加入 "XXXX"，但解码器还没看到它。
            # 解码器会先输出 "XXX"，然后收到 "XXXX" 的码字，发现它不在字典中，
            # 此时 k 就是 S + S[0]，即 "XXX" + "X" = "XXXX"。
            current_sequence = previous_sequence + previous_sequence[0]

        decoded_string += current_sequence

        # 4. 更新字典
        # 将 "前一个解码出的字符串 + 当前解码出的字符串的第一个字符" 添加到字典
        # 只有在 next_code 尚未达到字典最大限制时才添加
        dictionary[next_code] = previous_sequence + current_sequence[0]
        next_code += 1

        # 5. 更新 previous_sequence 为当前解码出的字符串
        previous_sequence = current_sequence

    return decoded_string

if __name__ == "__main__":
    # 检查命令行参数数量
    if len(sys.argv) != 2:
        exit("Usage:(Run with python lzw.py abracadabra)")

    input_text = sys.argv[1] # 确保只取第一个参数作为输入文本
    output_codes, _ = encode(input_text) # 编码时字典不再需要传递给 decode

    print("Encoded output codes: ", output_codes)
    print("Final dictionary size (after encode): ", len(_))

    print("Decoded string: ", end="")
    decoded_text = decode(output_codes)
    print(decoded_text)
