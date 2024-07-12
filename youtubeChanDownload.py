import os
import yt_dlp
import sys

# Set these variables
CHANNEL_URL = 'https://www.youtube.com/@PokerGO'
SAVE_PATH = 'downloads/'
MAX_DURATION = 5 * 60  # 5 minutes in seconds

def download_channel_videos(channel_url, save_path, max_duration):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
        'ignoreerrors': True,
        'extract_flat': 'in_playlist',
        'force_generic_extractor': False,
        'verbose': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            print(f"Attempting to extract info from: {channel_url}/videos")
            result = ydl.extract_info(f"{channel_url}/videos", download=False)
            
            if result is None:
                print("Error: Could not extract channel information.")
                return
            
            if 'entries' not in result:
                print("Error: No video entries found in the channel.")
                print("Extracted info:", result)
                return
            
            filtered_videos = []
            for entry in result['entries']:
                if entry and 'duration' in entry and entry['duration'] <= max_duration:
                    filtered_videos.append(entry)
            
            print(f"Found {len(filtered_videos)} videos under {max_duration} seconds")
            
            for video in filtered_videos:
                try:
                    video_url = video.get('url') or video.get('webpage_url')
                    if video_url:
                        print(f"Attempting to download: {video['title']} ({video['duration']} seconds)")
                        ydl.download([video_url])
                    else:
                        print(f"Skipping video '{video['title']}' with no URL")
                except Exception as e:
                    print(f"Error downloading {video.get('title', 'Unknown')}: {str(e)}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Traceback:", sys.exc_info())

def main():
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)
    
    print(f"Downloading videos from: {CHANNEL_URL}")
    print(f"Saving to: {SAVE_PATH}")
    print(f"Filtering videos up to {MAX_DURATION} seconds")
    
    download_channel_videos(CHANNEL_URL, SAVE_PATH, MAX_DURATION)
    
    print("Download process completed.")

if __name__ == "__main__":
    main()