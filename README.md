# video-tools
A set of tools for working with video workflows

# Create a conda Environment
conda create -n videoTools python=3.11
conda activate videoTools

# To extract just video from a video/audio file use this command
python extractVideo.py /path/to/your/video.mp4

# Compress video to a target file size in MB
python compress_video.py '/Users/Shared/Clients/EA/Highlights/EAH1.mp4' 100

