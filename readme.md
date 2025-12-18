# 🎬 AI YouTube Shorts Clipper (Gemini + GPU)

An **AI-powered automation tool** that converts long YouTube videos into engaging **vertical Shorts (9:16)**.
It downloads a YouTube video, extracts the transcript, uses **Google Gemini** to identify the most engaging moments, and generates high-quality portrait clips using **GPU-accelerated FFmpeg (NVENC)**.

---

## ✨ Features

- 📥 Download YouTube videos locally
- 📜 Automatically fetch video transcripts
- 🤖 Use **Google Gemini** to detect engaging moments
- ✂️ Generate multiple **60–90 second clips**
- 📱 Convert clips to **vertical 9:16 (1080×1920)** format
- ⚡ GPU-accelerated video processing (NVIDIA NVENC)
- 🧹 Auto-cleanup of source video after processing
- 🪟 Windows-safe (no file-lock issues)

---

## 🧠 How It Works

1. Paste a YouTube video URL
2. The video is downloaded as `<video_id>.mp4`
3. Transcript is fetched using YouTube Transcript API
4. Gemini analyzes the transcript and returns engaging timestamps
5. MoviePy + FFmpeg cut and crop clips to portrait format
6. Final clips are saved in the `clips/` directory
7. The original downloaded video is deleted automatically

---

## 📂 Output Structure

```

project-root/
├── clips/
│   ├── clip_title_1.mp4
│   ├── clip_title_2.mp4
│   └── ...
├── script.py
├── .env
└── README.md

```

---

## 🛠️ Requirements

### Software
- Python **3.9+**
- FFmpeg **with NVENC support**
- NVIDIA GPU (recommended)

### Python Libraries
```

google-generativeai
youtube-transcript-api
yt-dlp
moviepy
Pillow
python-dotenv

````

---

## ⚙️ Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/kiran-113/yt_clipper.git
cd yt_clipper
````

### 2️⃣ Create virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Setup

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_google_gemini_api_key
```

> You can get the API key from
> [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)

---

## 🚀 Usage

Run the script:

```bash
python script.py
```

Paste a YouTube video URL when prompted:

```text
Paste YouTube video URL: https://youtu.be/VIDEO_ID
```

Clips will be generated inside the `clips/` folder.

---

## ⚡ GPU Acceleration (Important)

This project uses **NVIDIA NVENC** for fast rendering.

### Verify FFmpeg NVENC support:

```bash
ffmpeg -encoders | findstr nvenc
```

If you see `h264_nvenc`, GPU acceleration is enabled.

---

## 🪟 Windows File Lock Fix

The script:

* Uses context managers for MoviePy
* Forces FFmpeg cleanup
* Delays deletion slightly

This prevents:

```
WinError 32: The process cannot access the file
```

---

## 🧪 Notes & Limitations

* Transcript must be available for the video
* Very long videos may hit Gemini context limits
* Accuracy of clips depends on transcript quality
* No YouTube upload functionality (by design)

---

## 🧩 Future Improvements (Optional)

* Auto subtitle burn-in
* Batch processing multiple videos
* Chunked transcript analysis
* Retry + JSON repair for Gemini output
* Web UI / Streamlit interface
* CLI arguments support

---

## 🏷️ Tags

```
python, youtube, shorts, ai, gemini, ffmpeg, nvenc, moviepy, automation
```

---

## 📜 License

MIT License — free to use, modify, and distribute.

---

## ⭐ Support

If you find this project useful:

* ⭐ Star the repo
* 🐛 Report issues
* 💡 Suggest improvements

Happy clipping! 🎉

```

conda create -n ytclipper  python=3.10

conda activate ytclipper

https://youtu.be/3tyaO-OE0K0?si=qDj6GbjJqJDd9Xkf
