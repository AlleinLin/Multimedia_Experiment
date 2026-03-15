import sys, socket

from ServerWorker import ServerWorker

class Server:
	"""
	RTSP服务器类。
	该服务器负责监听客户端的RTSP连接请求。
	对于每个接受的连接，它会创建一个 ServerWorker 线程来处理该客户端的请求。
	"""

	def main(self):
		"""
		服务器的主执行方法。
		此方法完成以下操作：
		1. 从命令行参数获取服务器监听的端口号。
		2. 创建一个TCP套接字 (rtspSocket) 用于监听RTSP连接。
		3. 将套接字绑定到指定的端口和所有可用的网络接口。
		4. 开始监听传入连接。
		5. 进入一个无限循环，等待并接受客户端连接。
		6. 对于每个新的客户端连接，创建一个 ServerWorker 实例来处理该连接上的RTSP通信，
		   并启动该 ServerWorker 的 run 方法。
		"""
		try:

			SERVER_PORT = int(sys.argv[1])
		except (IndexError, ValueError):
			print ("[用法: Server.py Server_port]\n")
			sys.exit(1)

		# 创建一个TCP套接字
		# AF_INET 表示使用IPv4地址族
		# SOCK_STREAM 表示使用TCP协议
		rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		try:
			# 将套接字绑定到本地地址和指定的端口
			# '' 表示绑定到所有可用的网络接口
			rtspSocket.bind(('', SERVER_PORT))
			print(f"RTSP服务器正在监听端口: {SERVER_PORT}")
		except socket.error as e:
			print(f"套接字绑定失败: {e}")
			sys.exit(1)

		# 开始监听TCP传入连接
		# 参数 5 表示在拒绝新连接之前，操作系统可以挂起的最大连接数
		rtspSocket.listen(5)

		while True:
			clientInfo = {} # 用于存储客户端信息的字典
			try:
				# 接受客户端的连接请求
				# rtspSocket.accept() 会阻塞，直到有新的连接到来
				# 它返回一个新的套接字对象 (用于与该特定客户端通信) 和客户端的地址信息
				client_socket, client_address = rtspSocket.accept()
				clientInfo['rtspSocket'] = (client_socket, client_address) # 存储客户端套接字和地址

				print(f"接受到来自 {client_address} 的新连接。")

				# 为接受的客户端连接创建一个 ServerWorker 实例
				# ServerWorker 负责处理该客户端的所有RTSP请求
				worker = ServerWorker(clientInfo)
				# 启动 ServerWorker 的 run 方法 (通常在一个新线程中运行，但这取决于 ServerWorker 的实现)
				worker.run()
				# 注意: 如果 ServerWorker.run() 是阻塞的，并且不是在新线程中运行，
				# 那么服务器将一次只能处理一个客户端。
				# 通常，ServerWorker().run() 会启动一个新线程来处理客户端，
				# 以便服务器可以立即返回到 accept() 等待下一个客户端。
			except KeyboardInterrupt:
				print("\n服务器被用户中断。正在关闭...")
				break # 捕获 Ctrl+C，退出循环
			except Exception as e:
				print(f"处理客户端连接时发生错误: {e}")
				# 根据错误类型，可能需要关闭 client_socket
				if 'client_socket' in locals() and client_socket:
					client_socket.close()

		rtspSocket.close()
		print("RTSP服务器已关闭。")

if __name__ == "__main__":
	server_instance = Server()
	server_instance.main()
