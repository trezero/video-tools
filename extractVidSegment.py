import subprocess
import sys

def trim_video(input_file):
    output_file = f"trimmed_{input_file}"
    subprocess.run(["ffmpeg", "-ss", "0", "-t", "30", "-i", input_file, "-c", "copy", "-copyts", output_file])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py input_video.mp4")
        sys.exit(1)

    input_file_name = sys.argv[1]
    trim_video(input_file_name)
