import sys
import subprocess
import os

def run_command(cmd):
    """ Runs a shell command and captures the output. """
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout, result.stderr
    except Exception as e:
        print(f"Error running command: {cmd}\n{e}")
        sys.exit(1)

def check_integrity(video_path):
    """ Checks file integrity using ffprobe. """
    print(f"Checking integrity of {video_path}...\n")
    cmd = f'ffprobe -v error -show_entries format=duration,bit_rate -show_streams -i "{video_path}"'
    stdout, stderr = run_command(cmd)
    if stderr:
        print(f"Integrity Check Failed: {stderr}\n")
        return False
    print(stdout)
    return True

def remux_video(video_path, output_path):
    """ Remuxes the video to fix container issues. """
    print(f"Remuxing {video_path} to {output_path}...\n")
    cmd = f'ffmpeg -i "{video_path}" -c copy "{output_path}"'
    _, stderr = run_command(cmd)
    if "error" in stderr.lower():
        print(f"Remuxing failed: {stderr}\n")
        return False
    return True

def extract_video(video_path, output_path):
    """ Extracts the video stream, ignoring errors. """
    print(f"Extracting video stream from {video_path} to {output_path}...\n")
    cmd = f'ffmpeg -err_detect ignore_err -i "{video_path}" -c:v copy -an "{output_path}"'
    _, stderr = run_command(cmd)
    if "error" in stderr.lower():
        print(f"Video extraction failed: {stderr}\n")
        return False
    return True

def extract_audio(video_path, output_path):
    """ Extracts the audio stream, ignoring errors. """
    print(f"Extracting audio stream from {video_path} to {output_path}...\n")
    cmd = f'ffmpeg -err_detect ignore_err -i "{video_path}" -c:a copy -vn "{output_path}"'
    _, stderr = run_command(cmd)
    if "error" in stderr.lower():
        print(f"Audio extraction failed: {stderr}\n")
        return False
    return True

def reencode_video(video_path, output_path):
    """ Re-encodes the video to a more compatible format. """
    print(f"Re-encoding {video_path} to {output_path}...\n")
    cmd = f'ffmpeg -i "{video_path}" -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k "{output_path}"'
    _, stderr = run_command(cmd)
    if "error" in stderr.lower():
        print(f"Re-encoding failed: {stderr}\n")
        return False
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python fixVid.py <video_file>")
        sys.exit(1)

    video_file = sys.argv[1]
    if not os.path.exists(video_file):
        print(f"File not found: {video_file}")
        sys.exit(1)

    base_name = os.path.splitext(video_file)[0]

    # Step 1: Check Integrity
    if not check_integrity(video_file):
        print("File integrity check failed. Proceeding with repairs...\n")

    # Step 2: Remux Video
    remuxed_video = f"{base_name}_remuxed.mp4"
    if remux_video(video_file, remuxed_video):
        print(f"Remuxing successful! Output: {remuxed_video}")
    else:
        print("Remuxing failed. Proceeding to extraction...")

    # Step 3: Extract Video & Audio
    extracted_video = f"{base_name}_video.mp4"
    extracted_audio = f"{base_name}_audio.aac"
    video_ok = extract_video(video_file, extracted_video)
    audio_ok = extract_audio(video_file, extracted_audio)

    # Step 4: Re-encode if necessary
    reencoded_video = f"{base_name}_fixed.mp4"
    if video_ok or audio_ok:
        if reencode_video(video_file, reencoded_video):
            print(f"Re-encoding successful! Output: {reencoded_video}")
        else:
            print("Re-encoding failed. Please check the file manually.")
    else:
        print("Could not extract usable video or audio. File may be corrupted.")

if __name__ == "__main__":
    main()
