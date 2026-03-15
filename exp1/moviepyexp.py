import os
from moviepy.config import change_settings
from moviepy.editor import VideoFileClip, TextClip, AudioFileClip, CompositeVideoClip, CompositeAudioClip

# --- 配置 FFMPEG 路径
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})

def edit_video_with_features(
    input_video_path: str,
    output_video_path: str,
    bg_music_path: str,
    student_id: str,
    subtitle_data: list
) -> None:
    """
    使用MoviePy编辑视频，实现添加字幕、配音和水印功能。
    对音频不进行处理
    Args:
        input_video_path (str): 输入原始视频文件的路径。
        output_video_path (str): 输出编辑后视频文件的路径。
        bg_music_path (str): 背景音乐文件的路径。
        student_id (str): 作为水印显示的学号文本。
        subtitle_data (list): 字幕数据列表。每个元素是一个元组 (start_time, end_time, text)，其中start_time和end_time是秒数。
    Returns:
        None: 视频编辑完成后，会在指定路径生成输出文件。
    """
    print(f"加载视频: {input_video_path}...")
    try:
        main_clip = VideoFileClip(input_video_path)
    except Exception as e:
        print(f"加载视频失败: {e}")
        return

    video_duration = main_clip.duration
    print(f"视频时长: {video_duration:.2f} 秒")

    # --- 1. 添加水印  ---
    print("正在添加水印...")
    watermark_text = f"© {student_id}"
    watermark_clip = TextClip(
        watermark_text,
        fontsize=30,
        color='white',
        font='SimHei',  # 黑体
        stroke_color='black',
        stroke_width=1
    )
    # 设置水印位置和持续时间
    watermark_clip = watermark_clip.set_position(("right", "bottom")).margin(
        right=20, bottom=20, opacity=0
    ).set_duration(video_duration).set_opacity(0.6) # 透明度，0.6

    # --- 2. 添加字幕 ---
    print("正在添加字幕...")
    subtitle_clips = []
    for start_time, end_time, text in subtitle_data:
        sub_clip = TextClip(
            text,
            fontsize=40,
            color='yellow',
            font='SimHei',
            stroke_color='black',
            stroke_width=1.5,
            bg_color='rgba(0,0,0,0.5)', # 半透明黑色背景
            method='caption',
            size=(main_clip.w * 0.8, None) # 字幕宽度是视频宽度的80%，高度自适应
        )
        sub_clip = sub_clip.set_start(start_time).set_end(end_time)
        sub_clip = sub_clip.set_position(("center", "bottom")).margin(bottom=50, opacity=0)
        subtitle_clips.append(sub_clip)

    # --- 3. 添加配音/背景音乐 (修改部分) ---
    print("正在添加背景音乐...")
    final_video_with_audio = main_clip # 保留原始视频的音频

    try:
        if os.path.exists(bg_music_path) and bg_music_path: # 确保路径有效
            background_audio = AudioFileClip(bg_music_path)

            # 获取原始视频的音频
            original_audio = main_clip.audio

            # CompositeAudioClip 会自动处理不同时长的音频，短的会在自己结束后停止。
            if background_audio.duration > video_duration:
                background_audio = background_audio.subclip(0, video_duration)

            # 混合原始音频和背景音乐
            # 降低背景音乐的音量，以免覆盖原始视频的声音
            # 如果 original_audio 为 None (原视频无声)，则直接用 background_audio
            if original_audio:
                combined_audio = CompositeAudioClip([original_audio, background_audio.volumex(0.3)])
            else:
                combined_audio = background_audio.volumex(0.3) # 如果原视频无声，直接用背景音乐

            # 将混合后的音频设置到视频剪辑
            final_video_with_audio = main_clip.set_audio(combined_audio)
        else:
            print("背景音乐文件不存在。")

    except Exception as e:
        print(f"加载或处理背景音乐失败: {e}。")
        # 此时 final_video_with_audio 仍保持为 main_clip，即保留原视频音频

    # --- 4. 合成所有视频元素 ---
    print("正在合成所有元素...")
    # 将主视频、水印和所有字幕剪辑组合在一起
    final_clips = [final_video_with_audio, watermark_clip] + subtitle_clips
    final_video = CompositeVideoClip(final_clips)

    # --- 5. 导出最终视频 ---
    print(f"导出视频: {output_video_path}...")
    try:
        final_video.write_videofile(
            output_video_path,
            codec="libx264",         # x264编码
            audio_codec="aac",       # aac编码
            fps=main_clip.fps,       # 保持帧率
            threads=4,               # 多线程
            preset="medium"          # 质量预设
        )
        print("导出完成！")
    except Exception as e:
        print(f"导出视频失败: {e}")

if __name__ == "__main__":
    # 定义文件路径
    INPUT_VIDEO_PATH = "input_video.mp4"
    OUTPUT_VIDEO_PATH = "output_video.mp4"
    BACKGROUND_MUSIC_PATH = "input_bgm.mp3"
    YOUR_STUDENT_ID = "学号: 2022212364"
    SUBTITLES = [
        (0.5, 3.0, "褚浩宇"),
        (3.5, 6.0, "这是一段字幕"),
        (6.5, 8.0, "2022212364")
    ]

    edit_video_with_features(
        INPUT_VIDEO_PATH,
        OUTPUT_VIDEO_PATH,
        BACKGROUND_MUSIC_PATH,
        YOUR_STUDENT_ID,
        SUBTITLES
    )

