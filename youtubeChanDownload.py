import os
import yt_dlp
import sys
import argparse

# Set these variables
SAVE_PATH = 'downloads/'
MAX_DURATION = 20 * 60  # 20 minutes in seconds
MAX_PAGES = 5

def get_channel_name(ydl, channel_url):
    info = ydl.extract_info(channel_url, download=False)
    return info.get('channel', 'Unknown_Channel').replace(' ', '_')

def download_channel_videos(channel_url, save_path, max_duration, max_pages):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'ignoreerrors': True,
        'extract_flat': 'in_playlist',
        'force_generic_extractor': False,
        'verbose': True,
        'playlistend': max_pages * 30,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            channel_name = get_channel_name(ydl, channel_url)
            channel_folder = os.path.join(save_path, channel_name)
            os.makedirs(channel_folder, exist_ok=True)
            
            ydl_opts['outtmpl'] = os.path.join(channel_folder, '%(title)s.%(ext)s')
            ydl = yt_dlp.YoutubeDL(ydl_opts)

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
            print(f"Saving videos to: {channel_folder}")
            
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
    parser = argparse.ArgumentParser(description="Download videos from a YouTube channel.")
    parser.add_argument("channel_url", help="URL of the YouTube channel")
    parser.add_argument("--save_path", default=SAVE_PATH, help="Path to save downloaded videos")
    parser.add_argument("--max_duration", type=int, default=MAX_DURATION, help="Maximum duration of videos to download (in seconds)")
    parser.add_argument("--max_pages", type=int, default=MAX_PAGES, help="Maximum number of pages to process")
    
    args = parser.parse_args()

    if not os.path.exists(args.save_path):
        os.makedirs(args.save_path)
    
    print(f"Downloading videos from: {args.channel_url}")
    print(f"Base save path: {args.save_path}")
    print(f"Filtering videos up to {args.max_duration} seconds")
    print(f"Limiting to a maximum of {args.max_pages} pages")
    
    download_channel_videos(args.channel_url, args.save_path, args.max_duration, args.max_pages)
    
    print("Download process completed.")

if __name__ == "__main__":
    main()