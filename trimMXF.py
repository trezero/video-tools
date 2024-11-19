import subprocess
import os

def get_frame_rate(video_path):
    """ Get the frame rate of the video using ffmpeg """
    cmd = [
        'ffmpeg', '-i', video_path, '-v', '0', '-select_streams', 'v:0', '-show_entries',
        'stream=r_frame_rate', '-of', 'default=noprint_wrappers=1:nokey=1'
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    frame_rate = result.stdout.strip()
    
    # Debugging step to see what is returned
    print(f"Frame rate output: {frame_rate}")
    
    if '/' in frame_rate:
        num, denom = frame_rate.split('/')
        return float(num) / float(denom)
    elif frame_rate.isdigit():
        return float(frame_rate)
    else:
        raise ValueError(f"Unexpected frame rate format: {frame_rate}")

def get_duration(video_path):
    """ Get the duration of the video in seconds using ffmpeg """
    cmd = [
        'ffmpeg', '-i', video_path, '-v', '0', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1'
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return float(result.stdout.strip())

def trim_video(video_path, output_path, frames_to_trim=50):
    """ Trim last 50 frames from the video """
    # Get frame rate and duration of the video
    frame_rate = get_frame_rate(video_path)
    duration = get_duration(video_path)

    # Calculate time to trim (frames to time in seconds)
    time_to_trim = frames_to_trim / frame_rate
    new_duration = duration - time_to_trim

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Trim video using ffmpeg
    cmd = [
        'ffmpeg', '-i', video_path, '-t', str(new_duration), '-c', 'copy', output_path
    ]
    subprocess.run(cmd)

if __name__ == '__main__':
    # Input and output paths
    input_video = 'sampleFiles/CSHPES07199.mxf'
    output_video = 'sampleFiles/CSHPES07199sm.mxf'

    # Call the trimming function
    trim_video(input_video, output_video)

