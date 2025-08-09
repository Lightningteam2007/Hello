import os
from moviepy.editor import VideoFileClip, CompositeVideoClip, ColorClip
import traceback
from config import Config

class VideoProcessor:
    @staticmethod
    def process_for_shorts(input_path):
        print(f"[INFO] Starting video processing: {input_path}")
        try:
            if not os.path.exists(input_path):
                print(f"[ERROR] Input video file does not exist: {input_path}")
                return None

            os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
            output_path = os.path.join(Config.OUTPUT_DIR, os.path.basename(input_path))

            clip = VideoFileClip(input_path)
            print(f"[INFO] Original video size: {clip.w}x{clip.h}, duration: {clip.duration}s")

            target_ratio = 9 / 16
            current_ratio = clip.w / clip.h
            print(f"[INFO] Current aspect ratio: {current_ratio:.3f}, Target aspect ratio: {target_ratio:.3f}")

            if current_ratio > target_ratio:
                # ویدیو عریض‌تره، حاشیه بالا و پایین اضافه می‌کنیم
                new_height = int(clip.w / target_ratio)
                padding = (new_height - clip.h) / 2
                processed_clip = CompositeVideoClip([
                    ColorClip((clip.w, new_height), color=(0, 0, 0), duration=clip.duration),
                    clip.set_position(("center", padding))
                ], size=(clip.w, new_height))
                print(f"[INFO] Added vertical black bars, new size: {clip.w}x{new_height}")
            else:
                # ویدیو بلندتره، حاشیه چپ و راست اضافه می‌کنیم
                new_width = int(clip.h * target_ratio)
                padding = (new_width - clip.w) / 2
                processed_clip = CompositeVideoClip([
                    ColorClip((new_width, clip.h), color=(0, 0, 0), duration=clip.duration),
                    clip.set_position((padding, "center"))
                ], size=(new_width, clip.h))
                print(f"[INFO] Added horizontal black bars, new size: {new_width}x{clip.h}")

            # تغییر سایز نهایی برای شورتز
            processed_clip = processed_clip.resize(height=1920)
            print(f"[INFO] Resized video height to 1920, final size: {processed_clip.w}x{processed_clip.h}")

            # نوشتن ویدیو خروجی
            processed_clip.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                fps=60,
                preset='ultrafast',
                threads=4,
                bitrate="8000k",
                verbose=False,
                logger=None
            )
            print(f"[INFO] Video processed and saved to: {output_path}")

            clip.close()
            processed_clip.close()
            return output_path

        except Exception as e:
            print(f"[ERROR] Error processing video: {e}")
            print(traceback.format_exc())
            return None
