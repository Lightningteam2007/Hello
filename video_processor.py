import os
import numpy as np
from moviepy.editor import *
from moviepy.video.fx.all import margin
from config import Config

class VideoProcessor:
    @staticmethod
    def process_for_shorts(input_path):
        try:
            os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
            output_path = os.path.join(Config.OUTPUT_DIR, os.path.basename(input_path))
            
            clip = VideoFileClip(input_path)
            
            # محاسبه نسبت‌ها
            target_ratio = 9/16
            current_ratio = clip.w / clip.h
            
            # ایجاد حاشیه سیاه بدون برش
            if current_ratio > target_ratio:
                new_height = int(clip.w / target_ratio)
                padding = (new_height - clip.h) / 2
                processed_clip = CompositeVideoClip([
                    ColorClip((clip.w, new_height), color=(0,0,0), duration=clip.duration),
                    clip.set_position(("center", padding))
                ], size=(clip.w, new_height))
            else:
                new_width = int(clip.h * target_ratio)
                padding = (new_width - clip.w) / 2
                processed_clip = CompositeVideoClip([
                    ColorClip((new_width, clip.h), color=(0,0,0), duration=clip.duration),
                    clip.set_position((padding, "center"))
                ], size=(new_width, clip.h))
            
            # بهینه‌سازی برای شورتز
            processed_clip = processed_clip.resize(height=1920)  # رزولوشن مناسب شورتز
            processed_clip.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                fps=60,
                preset='ultrafast',
                threads=4,
                bitrate="8000k"
            )
            
            return output_path
            
        except Exception as e:
            print(f"Error processing video: {e}")
            return None
