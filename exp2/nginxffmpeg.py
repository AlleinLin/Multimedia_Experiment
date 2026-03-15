import cv2
import numpy as np
import ffmpeg
from deepface import DeepFace
import face_recognition
from queue import Queue
import threading
import time

RTMP_URL = 'rtmp://192.168.75.135:1935/live/livestream'


class EmotionRecognizer:
    def __init__(self):
        self.emotion_map = {
            'happy': 'Happy',
            'sad': 'Sad',
            'angry': 'Angry',
            'fear': 'Fear',
            'surprise': 'Surprise',
            'neutral': 'Neutral',
            'disgust': 'Disgust'
        }
        try:
            print("正在预加载表情识别模型...")
            DeepFace.analyze(np.zeros((224, 224, 3), dtype=np.uint8), actions=['emotion'], enforce_detection=False,
                             silent=True)
            print("模型预加载完成。")
        except Exception as e:
            print(f"预加载失败: {e}")
            exit()

    def predict_emotion(self, face_image):
        if face_image is None or face_image.size == 0:
            return "无效人脸", 0.0

        try:
            result = DeepFace.analyze(face_image, actions=['emotion'], enforce_detection=False, silent=True)
            if not result:
                return "未检测到人脸", 0.0

            emotion = result[0]['dominant_emotion']
            confidence = result[0]['emotion'][emotion] / 100.0
            emotion_zh = self.emotion_map.get(emotion.lower(), '未知')
            return emotion_zh, confidence
        except Exception as e:
            print(f"表情分析错误: {e}")
            return "未知", 0.0

    def annotate_emotion(self, frame, emotion, confidence, left, top, right, bottom):
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        text = f"{emotion} ({confidence:.2%})"
        cv2.putText(frame, text, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)


def capture_thread(cap, frame_queue):
    """视频采集线程"""
    while True:
        ret, frame = cap.read()
        if not ret:
            frame_queue.put(None)  # 发送结束信号
            break
        frame_queue.put(frame.copy())

        time.sleep(0.01)

def processing_thread(emotion_recognizer, frame_queue, result_queue, process_every_n_frames):
    """处理线程：执行人脸检测和表情分析"""
    frame_counter = 0
    last_faces = []

    while True:
        frame = frame_queue.get()
        if frame is None:  # 结束信号
            result_queue.put(None)
            break

        frame_counter += 1

        if frame_counter % process_every_n_frames == 0:
            try:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_frame, model='hog')

                last_faces = []
                for (top, right, bottom, left) in face_locations:
                    face_image = frame[top:bottom, left:right]
                    if face_image.size > 0:
                        emotion, confidence = emotion_recognizer.predict_emotion(face_image)
                        last_faces.append((left, top, right, bottom, emotion, confidence))
            except Exception as e:
                print(f"处理错误: {e}")
                last_faces = []

        result_queue.put((frame.copy(), last_faces))


def streaming_thread(process, result_queue, display_queue):
    """推流线程：负责将处理后的帧发送到RTMP服务器"""
    while True:
        data = result_queue.get()
        if data is None:  # 结束信号
            break

        frame, faces = data

        # 在帧上绘制人脸信息
        for (left, top, right, bottom, emotion, confidence) in faces:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            text = f"{emotion} ({confidence:.2%})"
            cv2.putText(frame, text, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        cv2.putText(frame, "2022212364", (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

        try:
            process.stdin.write(frame.tobytes())
        except Exception as e:
            print(f"推流错误: {e}")
            break

        if not display_queue.full():
            display_queue.put(frame.copy())


def main():
    emotion_recognizer = EmotionRecognizer()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("无法打开摄像头")
        return

    # 降低分辨率以提升性能
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

    print(f"摄像头参数: {width}x{height} @ {fps:.1f} FPS")

    try:
        process = (
            ffmpeg
            .input('pipe:', format='rawvideo', pix_fmt='bgr24', s=f'{width}x{height}')
            .output(
                RTMP_URL,
                format='flv',
                vcodec='libx264',
                pix_fmt='yuv420p',
                preset='ultrafast',  # 最快编码速度
                tune='zerolatency',  # 零延迟调优
                crf=30,  # 更高CRF，画质更低但性能更好
                r=fps,  # 指定帧率
                g=int(fps),  # GOP大小等于帧率
                maxrate='2500k',  # 极低码率
                bufsize='5000k'
            )
            .overwrite_output()
            .run_async(pipe_stdin=True)
        )
        print(f"推流到: {RTMP_URL}")
    except Exception as e:
        print(f"FFmpeg启动失败: {e}")
        cap.release()
        return

    frame_queue = Queue(maxsize=5)  # 视频帧队列
    result_queue = Queue(maxsize=5)  # 处理结果队列
    display_queue = Queue(maxsize=1)  # 显示队列（保持最新一帧）

    process_every_n_frames = 5  # 每5帧处理一次

    # 启动线程
    threads = [
        threading.Thread(target=capture_thread, args=(cap, frame_queue), daemon=True),
        threading.Thread(target=processing_thread,
                         args=(emotion_recognizer, frame_queue, result_queue, process_every_n_frames), daemon=True),
        threading.Thread(target=streaming_thread, args=(process, result_queue, display_queue), daemon=True)
    ]

    for t in threads:
        t.start()

    print("开始运行，按 'q' 退出")
    cv2.namedWindow('Emotion Recognition', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Emotion Recognition', width, height)

    while True:
        # 显示最新帧
        if not display_queue.empty():
            frame = display_queue.get()
            cv2.imshow('Emotion Recognition', frame)

        # 按 'q' 退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 释放资源
    print("正在清理资源...")
    frame_queue.put(None)  # 发送结束信号

    # 等待线程结束
    for t in threads:
        t.join(timeout=2.0)

    cap.release()

    if process:
        process.stdin.close()
        process.wait()

    cv2.destroyAllWindows()
    print("程序已退出")


if __name__ == "__main__":
    main()
