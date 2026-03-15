import sys
'''
    维护一个全局的词典，不断地从字符流中提取新的字符串，通俗地理解为新词条，然后用词条的码字表示这个词条。
    这样一来，对字符流的编码就变成了用码字去替换字符流，生成码字流，从而达到压缩数据的目的。
    (1).初始化：
    在开始时，词典和当前前缀P都是空的。
    当前字符C ：字符流中的下一个字符。
    (2).判断P+C是否在词典中：
        1)如果“是”：用C扩展P，让P ：= P+C ；
        2)如果“否”：
            ① 输出与当前前缀P相对应的码字和当前字符C；
            ② 把字符串P+C 添加到词典中。
            ③ 令P ：=空值。
    (3).判断字符流中是否还有字符需要编码
        1)如果“是”：返回到步骤2。
        2)如果“否”：若当前前缀P不是空的，输出相应于当前前缀P的码字，然后结束编码。
'''

def encode(text):
    """
    使用LZ78算法对文本进行编码。
    将文本分解为(前缀的字典索引, 新字符)对。
    Args:
        text (str): 待编码的输入字符串。

    Returns:
        tuple: 包含三个元素的元组：
            - list[int]: 存储前缀的字典索引的列表。
            - list[str]: 存储与前缀配对的新字符的列表。
            - dict[str, int]: 编码过程中构建的字典，键是字符串，值是对应的索引。
    """
    mydict = dict()
    i = 0
    index = 1
    lstNumbers = []
    lstLetters = []
    current_prefix = ""

    for char in text:
        test_pattern = current_prefix + char

        # 检查 '当前前缀' + '当前字符' 是否已在字典中
        if test_pattern in mydict:
            # 如果是，说明找到了一个更长的匹配项，将当前字符添加到前缀中
            current_prefix = test_pattern
        else:
            # 如果 '当前前缀' + '当前字符' 不在字典中
            # 输出当前前缀的编码
            if current_prefix:
                lstNumbers.append(mydict[current_prefix])  # 将当前前缀对应的索引添加到数字列表中
            else:
                lstNumbers.append(0)  # 如果没有前缀（即第一个字符），则代码为0
            lstLetters.append(char)  # 将当前字符添加到字符列表中

            # 添加到字典
            mydict[test_pattern] = index
            index += 1  # 增加下一个字典条目的索引

            # 重置当前前缀
            current_prefix = ""

    # 如果还有未处理的最后一个匹配项，则输出其编码
    if current_prefix:
        lstNumbers.append(mydict[current_prefix])
        lstLetters.append("")  # 最后一个前缀后面没有新字符

    return lstNumbers, lstLetters, mydict  # 返回数字列表、字符列表和最终的字典


def decode(lstNumbers, lstLetters):
    """
    根据LZ78编码的数字和字符列表以及编码过程中生成的字典来解码文本。
    此解码器依赖于原始编码字典的顺序来逆向查找，
    Args:
        lstNumbers (list): 存储前缀的字典索引（数字代码）的列表。
        lstLetters (list): 存储与前缀配对的新字符的列表。
        mydict (dict): 编码过程中生成的字典，映射前缀字符串到其索引。

    Returns:
        None: 该函数直接打印解码后的字符串。
    """
    decoded_string_parts = []  # 存储解码后的字符串片段
    # 解码字典，用于存储索引到字符串的映射
    decoded_dictionary = {0: ""} # 0索引对应空字符串

    next_decode_index = 1

    for i in range(len(lstNumbers)):  # 遍历编码后的数字和字符对
        prefix_code = lstNumbers[i]
        new_char = lstLetters[i]

        decoded_prefix = decoded_dictionary[prefix_code] # 根据数字代码从解码字典中查找对应的字符串前缀
        current_decoded_word = decoded_prefix + new_char # 将解码出的前缀和新字符连接起来
        decoded_string_parts.append(current_decoded_word)

        # 仅当有新字符时才将新组合添加到字典，确保字典按 LZ78 方式增长
        # 如果 new_char 为空，表示这是最后一个前缀，它已经存在于字典中了。
        decoded_dictionary[next_decode_index] = current_decoded_word # 每次都会添加，这是LZ78解码的特性
        next_decode_index += 1


    return "".join(decoded_string_parts)


if __name__ == "__main__":
    if (len(sys.argv) != 2):
        exit("Usage:(Run with python lz78.py abracadabra)")
    stringToEncode = sys.argv[1]

    [lstNumbers, lstLetters, mydict] = encode(stringToEncode)

    print("Encoded string: ", end="")
    i = 0
    while i < len(lstNumbers):
        print("<{0}, {1}>".format(lstNumbers[i], lstLetters[i]), end=" ")
        i += 1
    print('\n')

    print("Decoded string: ", end="")
    decoded_text = decode(lstNumbers, lstLetters)
    print(decoded_text)
    print('\n')
