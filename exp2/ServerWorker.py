from random import randint
import sys, traceback, threading, socket
from VideoStream import VideoStream
from RtpPacket import RtpPacket


class ServerWorker:
    SETUP = 'SETUP'
    PLAY = 'PLAY'
    PAUSE = 'PAUSE'
    TEARDOWN = 'TEARDOWN'

    INIT = 0
    READY = 1
    PLAYING = 2
    state = INIT

    OK_200 = 0
    FILE_NOT_FOUND_404 = 1
    CON_ERR_500 = 2

    clientInfo = {}

    def __init__(self, clientInfo):
        """
		功能: 初始化 ServerWorker 类的实例。
		Args:
			self: ServerWorker 类的实例。
			clientInfo (dict): 包含客户端连接信息的字典，
								例如 {'rtspSocket': (socket, address), ...}。
		Returns: 无。
		"""
        self.clientInfo = clientInfo

    def run(self):
        """
		功能: 启动一个新的线程来接收和处理来自客户端的 RTSP 请求。
		Args:
			self: ServerWorker 类的实例。
		Returns: 无。
		"""
        threading.Thread(target=self.recvRtspRequest).start()

    def recvRtspRequest(self):
        """
		功能: 从客户端的 RTSP 套接字接收 RTSP 请求。
			  此函数在一个循环中运行，持续监听客户端请求。
		Args:
			self: ServerWorker 类的实例。
		Returns: 无。
		"""
        connSocket = self.clientInfo['rtspSocket'][0]
        while True:
            data = connSocket.recv(256)
            data = data.decode('utf-8')
            if data:
                print("Data received:\n" + data)
                self.processRtspRequest(data)

    def processRtspRequest(self, data):
        """
		功能: 处理从客户端接收到的 RTSP 请求字符串。
			  根据请求类型 (SETUP, PLAY, PAUSE, TEARDOWN) 执行相应的操作。
		Args:
			self: ServerWorker 类的实例。
			data (str): 从客户端接收到的原始 RTSP 请求字符串。
		Returns: 无。
		"""
        # Get the request type
        request = data.split('\n')
        line1 = request[0].split(' ')
        requestType = line1[0]

        # Get the media file name
        filename = line1[1]

        # Get the RTSP sequence number
        seq = request[1].split(' ')

        # Process SETUP request
        if requestType == self.SETUP:  # 如果需要setup
            if self.state == self.INIT:
                # Update state
                print("processing SETUP\n")
                try:
                    self.clientInfo['videoStream'] = VideoStream(filename)
                    self.state = self.READY  # writing your code here
                except IOError:
                    self.replyRtsp(self.FILE_NOT_FOUND_404, seq[1])

                # Generate a randomized RTSP session ID
                self.clientInfo['session'] = randint(100000, 999999)

                # Send RTSP reply
                self.replyRtsp(self.OK_200, seq[1])

                # Get the RTP/UDP port from the last line
                self.clientInfo['rtpPort'] = request[2].split(' ')[3]

        # Process PLAY request
        elif requestType == self.PLAY:
            if self.state == self.READY:
                print("processing PLAY\n")
                self.state = self.PLAYING  # writing your code here

                # Create a new socket for RTP/UDP
                self.clientInfo["rtpSocket"] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

                self.replyRtsp(self.OK_200, seq[1])

                # Create a new thread and start sending RTP packets
                self.clientInfo['event'] = threading.Event()
                self.clientInfo['worker'] = threading.Thread(target=self.sendRtp)
                self.clientInfo['worker'].start()

        # Process PAUSE request
        elif requestType == self.PAUSE:
            if self.state == self.PLAYING:
                print("processing PAUSE\n")
                self.state = self.READY  # writing your code here，暂停时回到READY状态能够再次PLAY

                self.clientInfo['event'].set()

                self.replyRtsp(self.OK_200, seq[1])

        # Process TEARDOWN request
        elif requestType == self.TEARDOWN:
            print("processing TEARDOWN\n")

            self.clientInfo['event'].set()

            self.replyRtsp(self.OK_200, seq[1])

            # Close the RTP socket
            self.clientInfo['rtpSocket'].close()

    def sendRtp(self):
        """
		功能: 通过 UDP 向客户端发送 RTP 数据包。
			  此函数在一个循环中运行，持续发送视频帧数据，
			  直到 PAUSE 或 TEARDOWN 请求被触发。
		Args:
			self: ServerWorker 类的实例。
		Returns: 无。
		"""
        while True:
            self.clientInfo['event'].wait(0.05)

            # Stop sending if request is PAUSE or TEARDOWN
            if self.clientInfo['event'].isSet():
                break

            data = self.clientInfo['videoStream'].nextFrame()
            if data:
                frameNumber = self.clientInfo['videoStream'].frameNbr()
                try:
                    address = self.clientInfo['rtspSocket'][1][0]
                    port = int(self.clientInfo['rtpPort'])
                    self.clientInfo['rtpSocket'].sendto(self.makeRtp(data, frameNumber), (address, port))
                except:
                    print("Connection Error")
            # print '-'*60
            # traceback.print_exc(file=sys.stdout)
            # print '-'*60

    def makeRtp(self, payload, frameNbr):
        """
		功能: 将视频帧数据封装成 RTP 数据包。
		Args:
			self: ServerWorker 类的实例。
			payload (bytes): 要发送的视频帧数据。
			frameNbr (int): 当前帧的序号。
		Returns:
			bytes: 封装好的 RTP 数据包。
		"""
        version = 2
        padding = 0
        extension = 0
        cc = 0
        marker = 0
        pt = 26  # MJPEG video type
        seqnum = frameNbr
        ssrc = 0

        rtpPacket = RtpPacket()

        rtpPacket.encode(version, padding, extension, cc, seqnum, marker, pt, ssrc, payload)

        return rtpPacket.getPacket()

    def replyRtsp(self, code, seq):
        """
		向客户端发送 RTSP 回复。
		Args:
			self: ServerWorker 类的实例。
			code (int): RTSP 响应状态码 (例如 OK_200, FILE_NOT_FOUND_404)。
			seq (str): 对应 RTSP 请求的序列号。
		Returns: 无。
		"""
        if code == self.OK_200:
            # print "200 OK"
            reply = 'RTSP/1.0 200 OK\nCSeq: ' + seq + '\nSession: ' + str(self.clientInfo['session'])
            connSocket = self.clientInfo['rtspSocket'][0]
            connSocket.send(reply.encode('utf-8'))

        # Error messages
        elif code == self.FILE_NOT_FOUND_404:
            print("404 NOT FOUND")
        elif code == self.CON_ERR_500:
            print("500 CONNECTION ERROR")
