import sys
from time import time

HEADER_SIZE = 12

class RtpPacket:
	"""
	表示一个RTP数据包。
	此类提供了编码和解码RTP数据包的方法，以及访问RTP头部字段的辅助方法。

	RTP头部结构 (RFC 3550):
	    0                   1                   2                   3
	    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
	   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
	   |V=2|P|X|  CC   |M|     PT      |       sequence number         |
	   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
	   |                           timestamp                           |
	   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
	   |           synchronization source (SSRC) identifier            |
	   +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+
	   |            contributing source (CSRC) identifiers             |
	   |                             ....                              |
	   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
	"""
	# 类级别的header变量，通常会被实例的self.header覆盖。
	# 在encode或decode调用前，它可能作为默认值或静态 размер 占位符。
	header = bytearray(HEADER_SIZE)

	def __init__(self):
		"""
		RtpPacket类的构造函数。
		目前不执行任何特定的初始化操作。
		"""
		pass

	def encode(self, version, padding, extension, cc, seqnum, marker, pt, ssrc, payload):
		"""
		使用头部字段和负载编码RTP数据包。

		参数:
			version (int): RTP协议版本 (通常为2)。
			padding (int):填充位 (0 或 1)。如果设置，数据包末尾包含额外的填充字节。
			extension (int): 扩展位 (0 或 1)。如果设置，RTP固定头部后跟一个头部扩展。
			cc (int): CSRC计数器，表示固定头部后CSRC标识符的数量。
			seqnum (int): 序列号，每个RTP数据包发送后递增1。
			marker (int): 标记位，其解释由具体的配置文件定义 (例如，视频帧的结束)。
			pt (int): 负载类型，指示RTP负载中数据的格式。
			ssrc (int): 同步源标识符，唯一标识RTP流的来源。
			payload (bytes): 数据包的负载数据。
		"""
		timestamp = int(time())  # 获取当前时间戳
		header = bytearray(HEADER_SIZE) # 初始化头部字节数组

		# 填充头部字节数组的各个字段:
		# 第一个字节 (header[0]):
		#   最高2位: 版本 (V)
		#   第3位: 填充位 (P)
		#   第4位: 扩展位 (X)
		#   最低4位: CSRC计数 (CC)
		header[0] = (version << 6) & 0xC0 # 设置版本号 (取高2位)
		header[0] = (header[0] | (padding << 5)) # 设置填充位 (第3位)
		header[0] = (header[0] | (extension << 4)) # 设置扩展位 (第4位)
		header[0] = (header[0] | (cc & 0x0F)) # 设置CSRC计数 (取低4位)

		# 第二个字节 (header[1]):
		#   最高1位: 标记位 (M)
		#   最低7位: 负载类型 (PT)
		header[1] = (marker << 7) & 0x80 # 设置标记位 (取高1位)
		header[1] = (header[1] | (pt & 0x7F)) # 设置负载类型 (取低7位)

		# 第三个和第四个字节 (header[2], header[3]): 序列号 (16位)
		header[2] = (seqnum >> 8) & 0xFF # 序列号的高8位
		header[3] = seqnum & 0xFF      # 序列号的低8位

		# 第五个到第八个字节 (header[4-7]): 时间戳 (32位)
		header[4] = (timestamp >> 24) & 0xFF # 时间戳的最高8位
		header[5] = (timestamp >> 16) & 0xFF
		header[6] = (timestamp >> 8) & 0xFF
		header[7] = timestamp & 0xFF         # 时间戳的最低8位

		# 第九个到第十二个字节 (header[8-11]): SSRC (32位)
		header[8] = (ssrc >> 24) & 0xFF # SSRC的最高8位
		header[9] = (ssrc >> 16) & 0xFF
		header[10] = (ssrc >> 8) & 0xFF
		header[11] = ssrc & 0xFF        # SSRC的最低8位

		# 设置RtpPacket实例的头部和负载
		self.header = header
		self.payload = payload

	def decode(self, byteStream):
		"""
		解码RTP数据包。
		从给定的字节流中解析RTP头部和负载。

		参数:
			byteStream (bytes): 包含RTP数据包的原始字节流。
		"""
		self.header = bytearray(byteStream[:HEADER_SIZE])
		self.payload = byteStream[HEADER_SIZE:]

	def version(self):
		"""
		返回RTP版本号。
		版本号位于头部的第一个字节的最高2位。
		"""
		return int(self.header[0] >> 6)

	def seqNum(self):
		"""
		返回序列号 (帧号)。
		序列号是一个16位字段。
		"""
		seqNum = (self.header[2] << 8) | self.header[3]
		return int(seqNum)

	def timestamp(self):
		"""
		返回时间戳。
		时间戳是一个32位字段。
		"""
		timestamp = (self.header[4] << 24) | (self.header[5] << 16) | (self.header[6] << 8) | self.header[7]
		return int(timestamp)

	def payloadType(self):
		"""
		返回负载类型。
		负载类型是一个7位字段。
		"""
		pt = self.header[1] & 127 # 01111111b
		return int(pt)

	def getPayload(self):
		"""
		返回数据包的负载。
		"""
		return self.payload

	def getPacket(self):
		"""
		返回完整的RTP数据包 (头部 + 负载)。
		"""
		return self.header + self.payload

