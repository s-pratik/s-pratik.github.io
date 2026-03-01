"""
extract_frames.py — Extract intro video frames for Pratik Sharma portfolio
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REQUIREMENTS:
  pip install ffmpeg-python
  + ffmpeg must be installed on your system:
      Windows : https://ffmpeg.org/download.html  (add to PATH)
      Mac     : brew install ffmpeg
      Linux   : sudo apt install ffmpeg

USAGE:
  1. Place this script in the same folder as your MP4 file
  2. Set INPUT_VIDEO below to your filename
  3. Run: python extract_frames.py
  4. A 'frames/' folder will be created with frame_0001.jpg ... frame_XXXX.jpg
  5. Put that 'frames/' folder next to your intro.html

"""

import subprocess
import os
import sys

# ── CONFIG ────────────────────────────────────────────────────────────────
INPUT_VIDEO  = "intro_video.mp4"  # ← your MP4 filename
OUTPUT_DIR   = "frames"
OUTPUT_WIDTH = 1920       # px wide — keeps 16:9 aspect ratio, sharp on all screens
JPEG_QUALITY = 2          # 1=best, 31=worst. 1-2 is near-lossless, file ~60-100KB/frame
SHARPENING   = True       # apply subtle unsharp mask to counter H.264 softness
# ─────────────────────────────────────────────────────────────────────────

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def extract_frames():
    if not check_ffmpeg():
        print("ERROR: ffmpeg not found.")
        print("  Mac:   brew install ffmpeg")
        print("  Win:   https://ffmpeg.org/download.html")
        print("  Linux: sudo apt install ffmpeg")
        sys.exit(1)

    if not os.path.exists(INPUT_VIDEO):
        print(f"ERROR: '{INPUT_VIDEO}' not found.")
        print("  Make sure the MP4 is in the same folder as this script,")
        print("  or update INPUT_VIDEO at the top of the script.")
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Build ffmpeg filter chain
    scale_filter = f"scale={OUTPUT_WIDTH}:-2:flags=lanczos"
    if SHARPENING:
        vf = f"{scale_filter},unsharp=5:5:1.0:3:3:0.3"
    else:
        vf = scale_filter

    output_pattern = os.path.join(OUTPUT_DIR, "frame_%04d.jpg")

    cmd = [
        "ffmpeg",
        "-i", INPUT_VIDEO,
        "-vf", vf,
        "-q:v", str(JPEG_QUALITY),
        output_pattern,
        "-y"
    ]

    print(f"\n{'='*55}")
    print(f"  Input  : {INPUT_VIDEO}")
    print(f"  Output : {OUTPUT_DIR}/frame_XXXX.jpg")
    print(f"  Width  : {OUTPUT_WIDTH}px (height auto from aspect ratio)")
    print(f"  Quality: q:v {JPEG_QUALITY} (near-lossless)")
    print(f"  Sharpen: {'yes' if SHARPENING else 'no'}")
    print(f"{'='*55}\n")
    print("Extracting frames... (this takes ~30-60 seconds)\n")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("ERROR during extraction:")
        print(result.stderr)
        sys.exit(1)

    # Count output frames
    frames = sorted([
        f for f in os.listdir(OUTPUT_DIR)
        if f.startswith("frame_") and f.endswith(".jpg")
    ])
    total = len(frames)

    if total == 0:
        print("ERROR: No frames were extracted. Check your video file.")
        sys.exit(1)

    # Calculate sizes
    sizes = [os.path.getsize(os.path.join(OUTPUT_DIR, f)) for f in frames]
    total_mb = sum(sizes) / 1024 / 1024
    avg_kb   = sum(sizes) / len(sizes) / 1024

    print(f"{'='*55}")
    print(f"  Done!")
    print(f"  Frames extracted : {total}")
    print(f"  Average size     : {avg_kb:.0f} KB per frame")
    print(f"  Total size       : {total_mb:.1f} MB")
    print(f"  Output folder    : ./{OUTPUT_DIR}/")
    print(f"{'='*55}\n")
    print("Next steps:")
    print(f"  1. Open intro.html and set:  const TOTAL_FRAMES = {total};")
    print(f"  2. Deploy the 'frames/' folder alongside intro.html")
    print(f"  3. Done!\n")

if __name__ == "__main__":
    extract_frames()
