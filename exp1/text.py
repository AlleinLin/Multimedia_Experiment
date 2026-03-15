from moviepy.editor import VideoFileClip, TextClip, AudioFileClip, CompositeVideoClip, CompositeAudioClip

from moviepy.video.VideoClip import TextClip
video = VideoFileClip("./movie.mp4")

# 制作文字，指定文字大小和颜色
txt_clip = (TextClip("20222123283")
            .set_position(lambda t: (10, 30))
            .set_duration(video.duration))

result = CompositeVideoClip([video, txt_clip])
mp3path = './audio.mp3'

audio_clip = AudioFileClip(mp3path)
video = video.set_audio(audio_clip)

result.write_videofile("./movie.mp4", fps=50)  # fps:视频文件中每秒的帧数

