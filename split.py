import os
import random
import subprocess

#gemini also did this part

VIDEO_DIR = "video"
OUTPUT_DIR = "source samples"
VALID_EXTS = (".mp4", ".mkv", ".avi", ".mov", ".webm")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_duration(file_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())

def split_video(file_name):
    input_path = os.path.join(VIDEO_DIR, file_name)
    try:
        total_duration = get_duration(input_path)
    except Exception as e:
        print(f"could not probe {file_name}: {e}")
        return

    current_time = 0.0
    clip_idx = 0
    saved_count = 0

    base_name = os.path.splitext(file_name)[0]

    while current_time < total_duration:
        clip_len = round(random.uniform(0.5, 3.0), 2)
        if current_time + clip_len > total_duration:
            clip_len = total_duration - current_time

        if clip_len < 0.2:
            break

        out_name = f"{base_name}_chunk_{clip_idx:04d}.mp4"
        out_path = os.path.join(OUTPUT_DIR, out_name)

        # switched -c:v to mpeg4 (native ffmpeg codec) so missing libx264 won't break execution
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(current_time),
            "-i", input_path,
            "-t", str(clip_len),
            "-c:v", "mpeg4",
            "-q:v", "2",
            "-c:a", "aac",
            out_path
        ]
        
        res = subprocess.run(cmd, capture_output=True, text=True)
        
        if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
            saved_count += 1
        else:
            print(f"failed clip {clip_idx}: {res.stderr[-200:] if res.stderr else 'unknown error'}")

        current_time += clip_len
        clip_idx += 1

    print(f"{file_name} was divided into {saved_count} chunks")

def main():
    if not os.path.exists(VIDEO_DIR):
        print(f"uhhh you forgot the {VIDEO_DIR}")
        return

    videos = [f for f in os.listdir(VIDEO_DIR) if f.lower().endswith(VALID_EXTS)]
    if not videos:
        print("maybe you need to find and save some videos first")
        return

    for v in videos:
        split_video(v)

if __name__ == "__main__":
    main()
