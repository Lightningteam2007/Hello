import os
import traceback
import subprocess
from config import Config
from PIL import Image
from PIL.Image import Resampling  # برای نسخه‌های جدید Pillow

try:
    from moviepy.editor import VideoFileClip, CompositeVideoClip, ColorClip
except ImportError:
    raise ImportError("لطفاً کتابخانه moviepy را با دستور زیر نصب کنید: pip install moviepy==1.0.3")

class VideoProcessor:
    @staticmethod
    def validate_video_file(input_path):
        """بررسی صحت فایل ویدیو"""
        try:
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"فایل ویدیو یافت نشد: {input_path}")
            
            if os.path.getsize(input_path) == 0:
                raise ValueError("فایل ویدیو خالی است!")
            
            cmd = ['ffprobe', '-v', 'error', '-i', input_path]
            result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            
            if result.returncode != 0:
                raise ValueError(f"فایل ویدیو نامعتبر است: {result.stderr.decode()}")
            
            return True
        except Exception as e:
            print(f"❌ خطا در بررسی فایل ویدیو: {str(e)}")
            return False

    @staticmethod
    def process_for_shorts(input_path):
        print(f"⚙️ در حال پردازش ویدیو: {input_path}")
        
        try:
            if not VideoProcessor.validate_video_file(input_path):
                raise ValueError("فایل ویدیو نامعتبر است")
            
            os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
            output_path = os.path.join(Config.OUTPUT_DIR, f"processed_{os.path.basename(input_path)}")
            
            clip = VideoFileClip(input_path)
            print(f"📏 اندازه اصلی: {clip.w}x{clip.h}, مدت: {clip.duration}ثانیه")
            
            # پردازش نسبت ابعاد
            target_ratio = 9 / 16
            current_ratio = clip.w / clip.h
            
            if abs(current_ratio - target_ratio) < 0.01:
                processed_clip = clip
                print("🔵 نسبت ابعاد مناسب است - بدون تغییر")
            elif current_ratio > target_ratio:
                new_height = int(clip.w / target_ratio)
                padding = (new_height - clip.h) / 2
                processed_clip = CompositeVideoClip([
                    ColorClip((clip.w, new_height), color=(0, 0, 0), duration=clip.duration),
                    clip.set_position(("center", padding))
                ], size=(clip.w, new_height))
                print("🔳 حاشیه عمودی اضافه شد")
            else:
                new_width = int(clip.h * target_ratio)
                padding = (new_width - clip.w) / 2
                processed_clip = CompositeVideoClip([
                    ColorClip((new_width, clip.h), color=(0, 0, 0), duration=clip.duration),
                    clip.set_position((padding, "center"))
                ], size=(new_width, clip.h))
                print("🔲 حاشیه افقی اضافه شد")
            
            # تغییر اندازه با روش سازگار با نسخه‌های جدید Pillow
            try:
                # روش جدید برای نسخه‌های جدید Pillow
                processed_clip = processed_clip.resize(height=Config.TARGET_HEIGHT)
            except Exception as resize_error:
                print(f"⚠️ خطا در تغییر اندازه: {resize_error}")
                raise
            
            # ذخیره ویدیو
            processed_clip.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                fps=Config.TARGET_FPS,
                preset='ultrafast',
                threads=4,
                bitrate=Config.BITRATE,
                logger=None
            )
            
            print(f"✅ ویدیو پردازش شده در: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ خطا در پردازش ویدیو: {str(e)}")
            print(traceback.format_exc())
            return None
