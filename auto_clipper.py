import os
import json
import re
import time
import gc
from dotenv import load_dotenv
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
from PIL import Image
from moviepy.editor import VideoFileClip

# ------------------ PATCHES ------------------
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

# Force system ffmpeg (GPU capable)
os.environ["IMAGEIO_FFMPEG_EXE"] = "ffmpeg"

# ------------------ CONFIG ------------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ Missing GEMINI_API_KEY in .env")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

DEFAULT_OUTPUT_DIR = "clips"

# ------------------ OUTPUT DIRECTORY ------------------
def get_output_directory():
    user_path = input(
        f"Enter directory to save clips (press Enter for '{DEFAULT_OUTPUT_DIR}'): "
    ).strip()

    if not user_path:
        print(f"📁 Using default directory: {DEFAULT_OUTPUT_DIR}")
        return DEFAULT_OUTPUT_DIR

    if not os.path.exists(user_path):
        try:
            os.makedirs(user_path, exist_ok=True)
            print(f"📁 Created directory: {user_path}")
            return user_path
        except Exception:
            print(f"⚠️ Invalid path. Using default: {DEFAULT_OUTPUT_DIR}")
            return DEFAULT_OUTPUT_DIR

    return user_path

# ------------------ DOWNLOAD VIDEO ------------------
def download_youtube(video_url, video_id):
    output_path = f"{video_id}.mp4"
    print("📥 Downloading video...")

    ydl_opts = {
        "outtmpl": output_path,
        "format": "mp4",
        "quiet": False
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    print("✅ Video downloaded:", output_path)
    return output_path

# ------------------ TRANSCRIPT ------------------
def get_transcript(video_id):
    print("📜 Fetching transcript...")
    return YouTubeTranscriptApi().fetch(video_id)

def transcript_to_text(transcript):
    return " ".join([entry.text for entry in transcript])

# ------------------ GEMINI: ENGAGING CLIPS ------------------
def get_engaging_clips(text):
    prompt = f"""
You are a strict JSON-only generator.

Analyze this transcript and extract the most engaging moments.

Return ONLY a valid JSON array.
Each clip must contain:
{{
  "title": "",
  "start_time": 0,
  "end_time": 0,
  "reason": "",
  "text": ""
}}

Rules:
- Each clip must be 60–90 seconds
- Decide the number of clips yourself
- No markdown
- No explanations
- Only JSON array

Transcript:
{text}
"""
    print("🤖 Sending transcript to Gemini...")
    raw = model.generate_content(prompt).text.strip()

    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if not match:
        raise ValueError("❌ Invalid Gemini output")

    clips = json.loads(match.group())
    print(f"✅ Gemini returned {len(clips)} clips")
    return clips

# ------------------ CUT VIDEO (GPU ENABLED + COLOR FIX) ------------------
def cut_clip(video_file, start, end, output_file):
    print(f"✂️ Cutting clip: {output_file}")

    with VideoFileClip(video_file) as video:
        clip = video.subclip(start, end)
        w, h = clip.size

        target_w = h * 9 / 16
        if target_w < w:
            x1 = (w - target_w) / 2
            clip = clip.crop(x1=x1, x2=x1 + target_w)

        clip = clip.resize((1080, 1920))

        clip.write_videofile(
            output_file,
            codec="h264_nvenc",
            audio_codec="aac",
            preset="fast",
            ffmpeg_params=[
                "-pix_fmt", "yuv420p",
                "-colorspace", "bt709",
                "-color_primaries", "bt709",
                "-color_trc", "bt709",
                "-rc", "vbr",
                "-cq", "19"
            ],
            threads=0
        )

        clip.close()

# ------------------ CLEANUP ------------------
def cleanup_files(*paths):
    time.sleep(1)
    gc.collect()

    for path in paths:
        try:
            if os.path.exists(path):
                os.remove(path)
                print(f"🧹 Removed file: {path}")
        except Exception as e:
            print(f"⚠️ Cleanup failed for {path}: {e}")

# ------------------ MAIN WORKFLOW ------------------
def process(video_url, output_dir):
    video_id = video_url.replace("https://youtu.be/", "").split("?")[0]

    video_path = download_youtube(video_url, video_id)
    transcript = get_transcript(video_id)
    text = transcript_to_text(transcript)
    clips = get_engaging_clips(text)

    os.makedirs(output_dir, exist_ok=True)

    with VideoFileClip(video_path) as probe:
        video_duration = probe.duration

    for i, clip in enumerate(clips):
        start = clip["start_time"]
        end = min(start + 90, video_duration)
        if end - start < 60:
            end = min(start + 60, video_duration)

        safe_title = re.sub(r"[^\w\s-]", "", clip["title"]).strip().replace(" ", "_")
        filename = os.path.join(
            output_dir, f"{safe_title or f'clip_{i+1}'}.mp4"
        )

        cut_clip(video_path, start, end, filename)

    cleanup_files(video_path)

    print("\n🎉 All clips generated successfully!")
    return clips

# ------------------ RUN SCRIPT ------------------
if __name__ == "__main__":
    url = input("Paste YouTube video URL: ")
    output_dir = get_output_directory()
    process(url, output_dir)
