import os
import sys
import subprocess

def fix_video(input_file):
    # Ensure the input file exists
    if not os.path.exists(input_file):
        print(f"Error: The file '{input_file}' does not exist.")
        return
    
    # Generate output filenames
    base_name = os.path.splitext(input_file)[0]
    audio_file = f"{base_name}_audio.aac"
    fixed_audio = f"{base_name}_fixed.aac"
    output_file = f"{base_name}_fixed.mp4"

    # Step 1: Extract audio
    print("Extracting audio...")
    extract_cmd = [
        "ffmpeg", "-y", "-i", input_file, 
        "-vn", "-acodec", "copy", audio_file
    ]
    subprocess.run(extract_cmd, check=True)

    # Step 2: Convert audio to standard AAC-LC
    print("Fixing audio...")
    fix_audio_cmd = [
        "ffmpeg", "-y", "-i", audio_file, 
        "-acodec", "aac", "-b:a", "128k", fixed_audio
    ]
    subprocess.run(fix_audio_cmd, check=True)

    # Step 3: Remux the video with the fixed audio
    print("Remuxing video with fixed audio...")
    remux_cmd = [
        "ffmpeg", "-y", "-i", input_file, "-i", fixed_audio,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", output_file
    ]
    subprocess.run(remux_cmd, check=True)

    # Cleanup intermediate files
    os.remove(audio_file)
    os.remove(fixed_audio)

    print(f"Fixed video saved as: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fixVid.py <video_file>")
        sys.exit(1)

    fix_video(sys.argv[1])
