# 多媒体信息处理实验

本项目包含两个多媒体信息处理实验，涵盖了视频编辑、数据压缩算法以及流媒体传输等核心内容。

## 项目结构

```
媒体实验/
├── exp1/                    # 实验一：多媒体数据处理与压缩
│   ├── moviepyexp.py        # 视频编辑（水印、字幕、配音）
│   ├── lz77.py              # LZ77压缩算法实现
│   ├── lz78.py              # LZ78压缩算法实现
│   ├── lzw.py               # LZW压缩算法实现
│   ├── test_lz77.py         # LZ77测试
│   ├── test_lz78.py         # LZ78测试
│   ├── test_lzw.py          # LZW测试
│   ├── input_video.mp4      # 输入视频文件
│   ├── input_bgm.mp3        # 背景音乐文件
│   └── output_video.mp4     # 输出视频文件
│
└── exp2/                    # 实验二：视频流媒体传输
    ├── Server.py            # RTSP服务器
    ├── ServerWorker.py      # 服务器工作线程
    ├── Client.py            # 客户端（带GUI）
    ├── ClientLauncher.py    # 客户端启动器
    ├── RtpPacket.py         # RTP数据包处理
    ├── VideoStream.py       # 视频流处理
    ├── movie.Mjpeg          # 测试视频文件
    └── run.bat              # 启动脚本
```

---

## 实验一：多媒体数据处理与压缩

### 1.1 视频编辑 (moviepyexp.py)

使用 MoviePy 库实现视频编辑功能，支持：

- **水印添加**：在视频右下角添加半透明水印
- **字幕添加**：支持时间轴字幕，可自定义样式
- **背景音乐**：混合原始音频与背景音乐
- **视频合成**：将所有元素合成为最终视频

**使用方法：**

```python
python moviepyexp.py
```

**依赖：**
- moviepy
- ImageMagick（用于文字渲染）

### 1.2 压缩算法实现

#### LZ77算法 (lz77.py)

基于滑动窗口的压缩算法，将文本分解为 `(偏移量, 长度, 下一个字符)` 三元组。

**使用方法：**

```bash
python lz77.py "abracadabra"
```

#### LZ78算法 (lz78.py)

基于字典的压缩算法，将文本分解为 `(前缀索引, 新字符)` 对。

**使用方法：**

```bash
python lz78.py "abracadabra"
```

#### LZW算法 (lzw.py)

Lempel-Ziv-Welch算法，使用动态字典进行压缩。

**使用方法：**

```bash
python lzw.py "abracadabra"
```

---

## 实验二：视频流媒体传输

基于 RTSP/RTP 协议实现的视频流媒体系统。

### 2.1 系统架构

```
┌─────────────┐      RTSP (TCP)      ┌─────────────┐
│   Client    │◄────────────────────►│   Server    │
│  (GUI界面)   │                      │ (RTSP服务器) │
└─────────────┘      RTP (UDP)       └─────────────┘
     ▲          ◄────────────────          │
     │                                     │
     └───────────── 视频帧数据 ─────────────┘
```

### 2.2 协议支持

- **RTSP (Real Time Streaming Protocol)**：用于会话控制
  - SETUP：建立会话
  - PLAY：开始播放
  - PAUSE：暂停播放
  - TEARDOWN：结束会话

- **RTP (Real-time Transport Protocol)**：用于媒体数据传输
  - 支持序列号、时间戳、SSRC等字段
  - 支持负载类型标识

### 2.3 使用方法

**启动服务器：**

```bash
python Server.py <端口号>
```

**启动客户端：**

```bash
python ClientLauncher.py <服务器IP> <服务器端口> <RTP端口> <视频文件名>
```

**示例：**

```bash
# 终端1 - 启动服务器
python Server.py 5100

# 终端2 - 启动客户端
python ClientLauncher.py 127.0.0.1 5100 5000 movie.Mjpeg
```

### 2.4 客户端功能

- Setup：建立RTSP会话
- Play：开始播放视频流
- Pause：暂停播放
- Teardown：断开连接

---

## 依赖环境

### Python版本
- Python 3.8+

### 主要依赖库

```bash
pip install moviepy pillow
```

### 可选依赖
- ImageMagick（用于MoviePy文字渲染）

---
