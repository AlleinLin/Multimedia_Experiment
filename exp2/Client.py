from tkinter import *
from tkinter import messagebox as tkMessageBox
from PIL import Image, ImageTk
import socket, threading, sys, traceback, os

from RtpPacket import RtpPacket

CACHE_FILE_NAME = "cache-"
CACHE_FILE_EXT = ".jpg"


class Client:
    INIT = 0
    READY = 1
    PLAYING = 2
    state = INIT

    SETUP = 0
    PLAY = 1
    PAUSE = 2
    TEARDOWN = 3

    # Initiation..
    def __init__(self, master, serveraddr, serverport, rtpport, filename):
        """
		功能: 初始化客户端应用程序。
			  设置GUI，初始化RTSP连接参数和状态。
		Args:
			master: Tkinter的根窗口或顶级窗口。
			serveraddr (str): 服务器的IP地址。
			serverport (str): 服务器的RTSP端口号。
			rtpport (str): 客户端用于接收RTP数据包的端口号。
			filename (str): 请求播放的视频文件名。
		Returns:
			无
		"""
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.handler)
        self.createWidgets()
        self.serverAddr = serveraddr
        self.serverPort = int(serverport)
        self.rtpPort = int(rtpport)
        self.fileName = filename
        self.rtspSeq = 0
        self.sessionId = 0
        self.requestSent = -1
        self.teardownAcked = 0
        self.connectToServer()
        self.frameNbr = 0

    def createWidgets(self):
        """
		功能: 创建客户端GUI的各种控件（按钮、标签等）。
		Args:
			self: Client类的实例。
		Returns:
			无
		"""
        # Create Setup button
        self.setup = Button(self.master, width=20, padx=3, pady=3)
        self.setup["text"] = "Setup"
        self.setup["command"] = self.setupMovie
        self.setup.grid(row=1, column=0, padx=2, pady=2)

        # Create Play button
        self.start = Button(self.master, width=20, padx=3, pady=3)
        self.start["text"] = "Play"
        self.start["command"] = self.playMovie
        self.start.grid(row=1, column=1, padx=2, pady=2)

        # Create Pause button
        self.pause = Button(self.master, width=20, padx=3, pady=3)
        self.pause["text"] = "Pause"
        self.pause["command"] = self.pauseMovie
        self.pause.grid(row=1, column=2, padx=2, pady=2)

        # Create Teardown button
        self.teardown = Button(self.master, width=20, padx=3, pady=3)
        self.teardown["text"] = "Teardown"
        self.teardown["command"] = self.exitClient
        self.teardown.grid(row=1, column=3, padx=2, pady=2)

        # Create a label to display the movie
        self.label = Label(self.master, height=19)
        self.label.grid(row=0, column=0, columnspan=4, sticky=W + E + N + S, padx=5, pady=5)

    def setupMovie(self):
        """
		功能: 处理 "Setup" 按钮点击事件。
			  如果客户端处于 INIT 状态，则向服务器发送SETUP请求。
		Args:
			self: Client类的实例。
		Returns:
			无
		"""
        if self.state == self.INIT:
            self.sendRtspRequest(self.SETUP)

    def exitClient(self):
        """
		功能: 处理 "Teardown" 按钮点击事件。
			  向服务器发送TEARDOWN请求，并关闭GUI窗口，清理缓存文件。
		Args:
			self: Client类的实例。
		Returns:
			无
		"""
        self.sendRtspRequest(self.TEARDOWN)
        self.master.destroy()  # Close the gui window
        fname = CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT
        if os.path.exists(fname):
            os.remove(fname)  # Delete the cache image from video

    def pauseMovie(self):
        """
		功能: 处理 "Pause" 按钮点击事件。
			  如果客户端处于 PLAYING 状态，则向服务器发送PAUSE请求。
		Args:
			self: Client类的实例。
		Returns:
			无
		"""
        if self.state == self.PLAYING:
            self.sendRtspRequest(self.PAUSE)

    def playMovie(self):
        """
		功能: 处理 "Play" 按钮点击事件。
			  如果客户端处于 READY 状态，则启动一个新的线程来监听RTP数据包，
			  并向服务器发送PLAY请求。
		Args:
			self: Client类的实例。
		Returns:
			无
		"""
        if self.state == self.READY:
            # Create a new thread to listen for RTP packets
            threading.Thread(target=self.listenRtp).start()
            self.playEvent = threading.Event()
            self.playEvent.clear()
            self.sendRtspRequest(self.PLAY)

    def listenRtp(self):
        """
		功能: 监听来自服务器的RTP数据包。
			  接收到数据包后，解码RTP包，提取视频帧数据，
			  并将帧数据写入缓存文件，然后更新GUI显示。
		Args:
			self: Client类的实例。
		Returns:
			无
		"""
        while True:
            try:
                data = self.rtpSocket.recv(20480)
                if data:
                    rtpPacket = RtpPacket()
                    rtpPacket.decode(data)

                    currFrameNbr = rtpPacket.seqNum()
                    print("Current Seq Num: " + str(currFrameNbr))

                    if currFrameNbr > self.frameNbr:  # Discard the late packet
                        self.frameNbr = currFrameNbr
                        self.updateMovie(self.writeFrame(rtpPacket.getPayload()))
            except:
                # Stop listening upon requesting PAUSE or TEARDOWN
                if self.playEvent.isSet():
                    break

                # Upon receiving ACK for TEARDOWN request,
                # close the RTP socket
                if self.teardownAcked == 1:
                    # self.rtpSocket.shutdown(socket.SHUT_RDWR) # Or self.TEARDOWN if it means SHUT_RDWR
                    self.rtpSocket.shutdown(socket.SHUT_RDWR)
                    self.rtpSocket.close()
                    break

    def writeFrame(self, data):
        """
		功能: 将接收到的视频帧数据写入一个临时的图像文件。
		Args:
			self: Client类的实例。
			data (bytes): 视频帧的原始数据。
		Returns:
			str: 缓存图像文件的名称。
		"""
        cachename = CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT
        file = open(cachename, "wb")
        file.write(data)
        file.close()

        return cachename

    def updateMovie(self, imageFile):
        """
		功能: 更新GUI中的图像标签以显示新的视频帧。
		Args:
			self: Client类的实例。
			imageFile (str): 要显示的图像文件的路径。
		Returns:
			无
		"""
        photo = ImageTk.PhotoImage(Image.open(imageFile))
        self.label.configure(image=photo, height=288)
        self.label.image = photo

    def connectToServer(self):
        """
		功能: 连接到RTSP服务器。
			  创建一个TCP套接字并尝试连接到指定的服务器地址和端口。
		Args:
			self: Client类的实例。
		Returns:
			无
		"""
        self.rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.rtspSocket.connect((self.serverAddr, self.serverPort))
        except:
            tkMessageBox.showwarning('Connection Failed', 'Connection to \'%s\' failed.' % self.serverAddr)

    def sendRtspRequest(self, requestCode):
        """
		功能: 向服务器发送RTSP请求。
			  根据请求代码（SETUP, PLAY, PAUSE, TEARDOWN）构建并发送相应的RTSP消息。
		Args:
			self: Client类的实例。
			requestCode (int): RTSP请求的类型 (SETUP, PLAY, PAUSE, TEARDOWN)。
		Returns:
			无
		"""
        # -------------
        # TO COMPLETE
        # -------------

        """
        self.rtspSeq += 1: 对于每一个新的RTSP请求（SETUP, PLAY, PAUSE, TEARDOWN），客户端都会增加其RTSP序列号 (rtspSeq)。CSeq (Command Sequence number) 头部字段用于匹配请求和响应。服务器在回复时会包含相同的 CSeq 值。
        self.requestSent = ...: 这个变量记录了客户端刚刚发送了哪种类型的请求。这有助于后续在 recvRtspReply 方法中解析服务器响应时，知道这个响应是针对哪个请求的，并据此更新客户端状态。
        request = ...: 这是构建实际的RTSP请求字符串的地方。RTSP请求遵循HTTP类似的文本格式，包含请求行、头部字段，并以空行结束（这里没有请求体）。
        self.rtspSocket.send(request.encode('utf-8')): 构建好的请求字符串被编码为UTF-8字节流，并通过已建立的TCP套接字 (self.rtspSocket) 发送给服务器。
        """
        # Setup request
        if requestCode == self.SETUP and self.state == self.INIT:
            threading.Thread(target=self.recvRtspReply).start()
            self.rtspSeq += 1
            request = 'SETUP ' + self.fileName + ' RTSP/1.0\n'
            request += 'CSeq: ' + str(self.rtspSeq) + '\n'
            request += 'Transport: RTP/UDP; client_port= ' + str(self.rtpPort)
            self.requestSent = self.SETUP
        # 当请求为SETUP且客户端处于初始状态时执行此代码块。
        # 1. 启动一个新线程来异步接收服务器的RTSP回复，避免阻塞主GUI线程。
        # 2. 增加RTSP请求的序列号。
        # 3. 构建SETUP请求字符串，包括：
        #    - 请求行（SETUP方法、文件名、RTSP版本）。
        #    - CSeq头部（包含当前序列号）。
        #    - Transport头部（告知服务器客户端期望的传输协议RTP/UDP以及客户端用于接收RTP数据的端口号）。
        # 4. 记录当前发送的请求类型为SETUP。

        # Play request
        elif requestCode == self.PLAY and self.state == self.READY:
            self.rtspSeq += 1
            request = 'PLAY ' + self.fileName + ' RTSP/1.0\n'
            request += 'CSeq: ' + str(self.rtspSeq) + '\n'
            request += 'Session: ' + str(self.sessionId)
            self.requestSent = self.PLAY
        # 当请求为PLAY且客户端处于准备就绪（SETUP已完成）状态时执行此代码块。
        # 1. 增加RTSP请求的序列号。
        # 2. 构建PLAY请求字符串，包括：
        #    - 请求行（PLAY方法、文件名、RTSP版本）。
        #    - CSeq头部。
        #    - Session头部（包含由服务器在SETUP响应中分配的会话ID）。
        # 3. 记录当前发送的请求类型为PLAY。

        # Pause request
        elif requestCode == self.PAUSE and self.state == self.PLAYING:
            self.rtspSeq += 1
            request = 'PAUSE ' + self.fileName + ' RTSP/1.0\n'
            request += 'CSeq: ' + str(self.rtspSeq) + '\n'
            request += 'Session: ' + str(self.sessionId)
            self.requestSent = self.PAUSE
        # 当请求为PAUSE且客户端处于正在播放状态时执行此代码块。
        # 1. 增加RTSP请求的序列号。
        # 2. 构建PAUSE请求字符串，结构与PLAY请求类似，但方法为PAUSE，同样需要Session ID。
        # 3. 记录当前发送的请求类型为PAUSE。

        # Teardown request
        elif requestCode == self.TEARDOWN and not self.state == self.INIT:
            self.rtspSeq += 1
            request = 'TEARDOWN ' + self.fileName + ' RTSP/1.0\n'
            request += 'CSeq: ' + str(self.rtspSeq) + '\n'
            request += 'Session: ' + str(self.sessionId)
            self.requestSent = self.TEARDOWN
        # 当请求为TEARDOWN且客户端不处于初始状态（即会话已建立或正在进行）时执行此代码块。
        # 1. 增加RTSP请求的序列号。
        # 2. 构建TEARDOWN请求字符串，用于请求服务器终止当前会话，同样需要Session ID。
        # 3. 记录当前发送的请求类型为TEARDOWN。

        else:
            return
        # 如果传入的requestCode和当前客户端状态不满足上述任何条件组合，
        # 则不构建任何请求，函数直接返回。

        self.rtspSocket.send(request.encode('utf-8'))
        print('\nData sent:\n' + request)
        # 将最终构建好的RTSP请求字符串编码为UTF-8字节流，并通过TCP套接字发送给服务器。


    def recvRtspReply(self):
        """
		功能: 接收来自服务器的RTSP回复。
			  在一个循环中接收数据，直到收到TEARDOWN的确认或连接关闭。
		Args:
			self: Client类的实例。
		Returns:
			无
		"""
        while True:
            reply = self.rtspSocket.recv(1024).decode('utf-8')

            if reply:
                self.parseRtspReply(reply)

            # Close the RTSP socket upon requesting Teardown
            if self.requestSent == self.TEARDOWN:
                self.rtspSocket.shutdown(socket.SHUT_RDWR)
                self.rtspSocket.close()
                break

    def parseRtspReply(self, data):
        """
		功能: 解析来自服务器的RTSP回复。
			  根据回复的状态码和内容更新客户端状态和会话ID。
		Args:
			self: Client类的实例。
			data (str): 从服务器接收到的原始RTSP回复字符串。
		Returns:
			无
		"""
        lines = data.split('\n')
        seqNum = int(lines[1].split(' ')[1])

        # Process only if the server reply's sequence number is the same as the request's
        if seqNum == self.rtspSeq:
            session = int(lines[2].split(' ')[1])
            # New RTSP session ID
            if self.sessionId == 0:
                self.sessionId = session

            # Process only if the session ID is the same
            if self.sessionId == session:
                if int(lines[0].split(' ')[1]) == 200:
                    if self.requestSent == self.SETUP:
                        # Update RTSP state.
                        self.state = self.READY

                        # Open RTP port.
                        self.openRtpPort()
                    elif self.requestSent == self.PLAY:
                        self.state = self.PLAYING
                    elif self.requestSent == self.PAUSE:
                        self.state = self.READY

                        # The play thread exits. A new thread is created on resume.
                        self.playEvent.set()
                    elif self.requestSent == self.TEARDOWN:
                        self.state = self.INIT

                        # Flag the teardownAcked to close the socket.
                        self.teardownAcked = 1

    def openRtpPort(self):
        """
		功能: 打开RTP端口以接收视频数据。
			  创建一个UDP套接字，并将其绑定到客户端指定的RTP端口。
			  设置套接字超时。
		Args:
			self: Client类的实例。
		Returns:
			无
		"""
        # Create a new datagram socket to receive RTP packets from the server
        self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Set the timeout value of the socket to 0.5sec
        self.rtpSocket.settimeout(0.5)

        try:
            # Bind the socket to the address using the RTP port given by the client user
            self.rtpSocket.bind(("", self.rtpPort))  # empty string for address means bind to all available interfaces
        except:
            tkMessageBox.showwarning('Unable to Bind', 'Unable to bind PORT=%d' % self.rtpPort)

    def handler(self):
        """
		功能: 处理GUI窗口关闭事件（例如点击关闭按钮）。
			  先暂停电影播放，然后询问用户是否确定退出。
			  如果用户确认，则执行退出客户端的操作；否则，恢复播放。
		Args:
			self: Client类的实例。
		Returns:
			无
		"""
        self.pauseMovie()
        if tkMessageBox.askokcancel("Quit?", "Are you sure you want to quit?"):
            self.exitClient()
        else:  # When the user presses cancel, resume playing.
            # Note: playMovie() checks state == READY. If pause was successful, state is READY.
            self.playMovie()
