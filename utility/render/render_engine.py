import time
import os
import tempfile
import zipfile
import platform
import subprocess
from moviepy.editor import (AudioFileClip, CompositeVideoClip, CompositeAudioClip, ImageClip,
                            TextClip, VideoFileClip)
from moviepy.audio.fx.audio_loop import audio_loop
from moviepy.audio.fx.audio_normalize import audio_normalize
import requests

def download_file(url, filename):
    with open(filename, 'wb') as f:
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        f.write(response.content)

def search_program(program_name):
    try: 
        search_cmd = "where" if platform.system() == "Windows" else "which"
        return subprocess.check_output([search_cmd, program_name]).decode().strip()
    except subprocess.CalledProcessError:
        return None

def get_program_path(program_name):
    program_path = search_program(program_name)
    return program_path

def get_output_media(audio_file_path, timed_captions, background_video_data, video_server, language):
    OUTPUT_FILE_NAME = f"rendered_video_{language}.mp4"
    SEGMENT_DURATION = 60  # Process in 1-minute segments

    audio_clip = AudioFileClip(audio_file_path)
    total_duration = audio_clip.duration

    segments = []
    for i in range(0, int(total_duration), SEGMENT_DURATION):
        start = i
        end = min(i + SEGMENT_DURATION, total_duration)
        
        segment_audio = audio_clip.subclip(start, end)
        segment_captions = [cap for cap in timed_captions if start <= cap[0][0] < end]
        segment_background = [bg for bg in background_video_data if start <= bg[0][0] < end]
        
        segment = create_video_segment(segment_audio, segment_captions, segment_background, start, language)
        segments.append(segment)

    final_video = concatenate_videoclips(segments)
    final_video.write_videofile(OUTPUT_FILE_NAME, codec='libx264', audio_codec='aac', fps=25, preset='veryfast')

    return OUTPUT_FILE_NAME

def create_video_segment(audio, captions, background, start_time, language):
    visual_clips = []
    
    for (t1, t2), video_url in background:
        video_filename = tempfile.NamedTemporaryFile(delete=False).name
        download_file(video_url, video_filename)
        
        video_clip = VideoFileClip(video_filename)
        video_clip = video_clip.set_start(t1 - start_time).set_end(t2 - start_time)
        visual_clips.append(video_clip)
    
    for (t1, t2), text in captions:
        text_clip = TextClip(txt=text, fontsize=40, color="white", stroke_width=2, stroke_color="black", method="label")
        text_clip = text_clip.set_start(t1 - start_time).set_end(t2 - start_time)
        text_clip = text_clip.set_position(("center", "bottom"))
        visual_clips.append(text_clip)

    video = CompositeVideoClip(visual_clips)
    video.audio = audio
    video.duration = audio.duration

    return video
