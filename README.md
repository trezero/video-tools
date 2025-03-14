# Video Tools

This repository contains a collection of Python scripts designed to facilitate various video processing workflows. These tools can help with video compression, audio manipulation, frame extraction, YouTube downloads, face detection, and other media processing tasks.

## Tools Description

### Audio Processing Tools
- **extractAudio.py**: Extracts audio from a video file and saves it as a WAV file
- **compressAudio.py**: Compresses audio files while maintaining quality
- **fixAudio.py**: Repairs and fixes issues in audio files
- **mergeAudio.py**: Combines multiple audio files into a single file

### Video Processing Tools
- **compressVideo.py**: Compresses videos to a specified size while attempting to retain quality
- **createFrames.py**: Extracts individual frames from a video file
- **extractImagesFromVid.py**: Extracts images from specific points in a video
- **extractVidSegment.py**: Extracts a specific segment from a video file
- **extractVideo.py**: Extracts video without audio
- **fixVid.py**: Repairs and fixes issues in video files
- **trimMXF.py**: Trims MXF format video files
- **extract10Frames.py**: Extracts 10 evenly spaced frames from a video
- **extractProxyFiles.py**: Creates proxy (lower resolution) files from videos

### Test Video Generation
- **createTestVideo.py**: Generates a test video with timecode overlay and audio tones
- **createTestVid24.py**: Creates a test video with 24 audio tracks at different frequencies

### Face Detection Tools
- **faceDetectionTools/checkFaces.py**: Detects and analyzes faces in images/videos
- **faceDetectionTools/face_quality.py**: Assesses the quality of detected faces
- **faceDetectionTools/findPlayerFaces.py**: Specialized tool for detecting player faces
- **faceDetectionTools/generateTrainingFaces.py**: Generates face data for training

### YouTube Tools
- **youtubeChanDownload.py**: Downloads videos from a YouTube channel with customizable options
  - Supports filtering by video duration
  - Allows specifying save location
  - Usage: `python youtubeChanDownload.py <channel_url> [--save_path PATH] [--max_duration SECONDS]`

### File Management Tools
- **batchRename.py**: Batch renames files using a base filename and incremental numbering
  - Usage: `python batchRename.py <folder_path> <base_filename>`
  - Example: `python batchRename.py ./videos episode` will rename files to episode_001.ext, episode_002.ext, etc.
- **clean_filenames.py**: Cleans and standardizes filenames
- **cleanContacts.py**: Processes and cleans contact information files
- **mergeCSV.py**: Combines multiple CSV files into a single file

### System Administration Tools
- **genRemoteSSHKey.py**: Generates SSH keys for remote systems and updates local SSH config for passwordless authentication
  - Works on both Windows and Linux host systems
  - Connect to remote Linux systems and generate SSH keys
  - Options to use existing SSH keys or create new connection-specific keys
  - Automatically updates local SSH config file for easy connections
  - Usage: `python genRemoteSSHKey.py`

### Utility Tools
- **condaCheck.sh**: Checks for conda and Python 3.10 installation on Ubuntu 22 systems
  - Automatically installs Miniconda and Python 3.10 if not found
  - Usage: `./condaCheck.sh`
- **listAllRepos.py**: Fetches a list of GitHub repositories and writes them to a CSV file
- **llavaVideo.py**: Processes videos for LLaVA model analysis
- **scrapeAPIandCreateGPTdocs.py**: Generates documentation from API scraping
- **scrapeLinkedIN.py**: Tool for scraping LinkedIn data

## Prerequisites

Before running these scripts, you need to have Python installed on your system along with the following packages:
- `moviepy`
- `opencv-python`
- `yt-dlp`
- `ffmpeg-python`
- `numpy`
- `pandas`
- `paramiko` (required for genRemoteSSHKey.py)

You can install the required packages using pip:
```bash
pip install -r requirements.txt
```

## Note
Some tools may require additional dependencies like `ffmpeg` to be installed on your system. Make sure to install any system-level dependencies before running the scripts.
