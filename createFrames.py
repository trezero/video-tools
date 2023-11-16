import cv2
import base64
import argparse

def create_frames(video_file_path):
    video = cv2.VideoCapture(video_file_path)
    frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
    base64Frames = []
    while video.isOpened():
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))
    video.release()
    print(len(base64Frames), "frames read.")
    return base64Frames, frame_count

def main():
    parser = argparse.ArgumentParser(description='Process a video file and convert frames to base64.')
    parser.add_argument('video_file_path', type=str, help='Path to the video file to process.')
    args = parser.parse_args()
    
    base64_frames, frame_count = create_frames(args.video_file_path)
    # Process the base64_frames as needed, or save to file, etc.
    # For now, we'll just print the frame count.
    print(f"Processed {frame_count} frames from the video.")

if __name__ == "__main__":
    main()
