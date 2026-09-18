import os
import random
import subprocess
import time

#let's say i collabed with gemini

SOURCE_DIR = "source samples"
OUTPUT_DIR = "output"
VALID_EXTS = (".mp4", ".mkv", ".avi", ".mov", ".webm")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def stitch_samples():
    samples = [f for f in os.listdir(SOURCE_DIR) if f.lower().endswith(VALID_EXTS)]
    if not samples:
        print("maybe you need to run split.py first")
        return

    sample_count = random.randint(5, 20)
    selected = random.choices(samples, k=min(sample_count, len(samples)))
    
    list_file = os.path.join(OUTPUT_DIR, "concat_list.txt")
    with open(list_file, "w", encoding="utf-8") as f:
        for s in selected:
            # absolute path formatted cleanly with forward slashes for ffmpeg concat demuxer
            full_path = os.path.abspath(os.path.join(SOURCE_DIR, s)).replace("\\", "/")
            # escape single quotes in file paths if present
            full_path = full_path.replace("'", "'\\''")
            f.write(f"file '{full_path}'\n")

    timestamp = int(time.time())
    out_path = os.path.join(OUTPUT_DIR, f"slop_{timestamp}.mp4")

    vf_filter = "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1"

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-vf", vf_filter,
        "-c:v", "mpeg4",
        "-q:v", "2",
        "-r", "30",
        "-c:a", "aac",
        "-ar", "44100",
        out_path
    ]

    # capture stdout/stderr so we can read error logs if execution fails
    res = subprocess.run(cmd, capture_output=True, text=True)

    if os.path.exists(list_file):
        os.remove(list_file)

    # verify the output file exists AND is greater than 0 bytes
    if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        print(f"fabricated some slop with {len(selected)} clips: {out_path}")
    else:
        print(f"i may have messed up since ffmpeg error:\n{res.stderr[-400:] if res.stderr else 'unknown error'}")

if __name__ == "__main__":
    stitch_samples()
