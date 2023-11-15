import sys
from moviepy.editor import VideoFileClip

def extract_audio(video_path):
    audio_path = video_path.rsplit('.', 1)[0] + '.wav'
    video_clip = VideoFileClip(video_path)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(audio_path)
    audio_clip.close()
    video_clip.close()
    print(f"Extracted audio to {audio_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extractAudio.py <video_file>")
    else:
        video_file_path = sys.argv[1]
        extract_audio(video_file_path)