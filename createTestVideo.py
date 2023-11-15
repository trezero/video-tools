import subprocess
import time

def generate_video_with_timecode(output_file="test_video_with_timecode-jp110723v4.mov"):
    # Get current timestamp for uniqueness
    timestamp = str(time.time())
    
    command = [
        "ffmpeg",
        "-f", "lavfi", "-i", "color=c=blue:s=1280x720:d=5",
        "-f", "lavfi", "-i", "aevalsrc=0.5*sin(440*2*PI*t)|0.5*sin(440*2*PI*t):s=44100:d=5",
        "-f", "lavfi", "-i", "aevalsrc=0.5*sin(550*2*PI*t)|0.5*sin(550*2*PI*t):s=44100:d=5",
        "-f", "lavfi", "-i", "aevalsrc=0.5*sin(660*2*PI*t)|0.5*sin(660*2*PI*t):s=44100:d=5",
        "-f", "lavfi", "-i", "aevalsrc=0.5*sin(770*2*PI*t)|0.5*sin(770*2*PI*t):s=44100:d=5",
        "-vf", f"drawtext=text='Test Video':fontsize=24:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2,drawtext=text='{timestamp}':fontsize=0:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
        "-timecode", "00:01:57:00",
        "-metadata:s:v:0", "timecode=00:01:57:00",
        "-c:a", "aac", 
        "-strict", "experimental",
        "-map", "0:v",
        "-map", "1:a",
        "-map", "2:a",
        "-map", "3:a",
        "-map", "4:a",
        "-y", output_file
    ]
    
    subprocess.run(command)

if __name__ == "__main__":
    generate_video_with_timecode()
