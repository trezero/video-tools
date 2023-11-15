import subprocess
import time

def generate_video_with_timecode(output_file="test_video_with_timecodeAnd24tr.mov"):
    # Get current timestamp for uniqueness
    timestamp = str(time.time())

    # Base command for video and text overlay
    command = [
        "ffmpeg",
        "-f", "lavfi", "-i", "color=c=blue:s=1280x720:d=5",
        "-vf", f"drawtext=text='Test Video':fontsize=24:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2,drawtext=text='{timestamp}':fontsize=0:fontcolor=white:x=0:y=0",
        "-timecode", "00:01:57:00",
        "-metadata:s:v:0", "timecode=00:01:57:00",
        "-c:v", "libx264",
    ]

    # Add audio tracks with different frequencies
    base_frequency = 440  # A4 note frequency in Hz
    for i in range(1, 25):  # 24 audio tracks
        frequency = base_frequency + (i * 10)  # Increment frequency by 10 Hz for each track
        command.extend([
            "-f", "lavfi", "-i", f"aevalsrc=0.5*sin({frequency}*2*PI*t):s=44100:d=5"
        ])

    # Map audio tracks
    for i in range(24):  # 24 audio tracks
        command.extend(["-map", str(i + 1)])

    # Global options for audio
    command.extend([
        "-c:a", "aac",
        "-strict", "experimental",
        "-y", output_file
    ])

    subprocess.run(command)

if __name__ == "__main__":
    generate_video_with_timecode()
