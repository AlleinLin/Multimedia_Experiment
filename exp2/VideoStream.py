class VideoStream:
	"""
	管理视频文件流。
	此类用于从指定的视频文件中逐帧读取数据。
	视频文件的格式假定为：每帧数据前有5个字节表示该帧的长度。
	"""
	def __init__(self, filename):
		"""
		VideoStream类的构造函数。

		参数:
			filename (str): 要读取的视频文件的路径。

		异常:
			IOError: 如果文件无法打开或读取。
		"""
		self.filename = filename
		try:
			self.file = open(filename, 'rb') # 以二进制只读模式打开文件
		except IOError: # 原代码是 except: 但更明确的 IOError 更好
			# 如果文件打开失败，则引发IOError异常
			raise IOError("无法打开视频文件: " + filename)
		self.frameNum = 0 # 初始化帧号计数器

	def nextFrame(self):
		"""
		获取视频流中的下一帧。
		首先读取5个字节来确定帧的长度，然后读取相应长度的帧数据。

		返回:
			bytes: 包含下一帧数据的字节串。如果到达文件末尾，则返回空字节串或None (取决于read的行为)。
		"""
		# 读取5个字节，这5个字节包含了当前帧的长度信息
		data = self.file.read(5)
		if data:
			# 将读取到的5字节长度信息转换为整数
			framelength = int(data)

			# 根据获取到的帧长度，读取当前帧的实际数据
			frame_data = self.file.read(framelength)
			self.frameNum += 1 # 帧号递增
			return frame_data # 返回帧数据
		else:
			# 如果读取不到数据 (文件末尾)，则返回None或空字节串
			return None # 或者 return b''，具体取决于期望的行为

	def frameNbr(self):
		"""
		获取当前已读取的帧号。

		返回:
			int: 当前帧的编号。
		"""
		return self.frameNum