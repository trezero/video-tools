import cv2
import os
import argparse
from pathlib import Path

def create_frames(video_file_path, fps):
    video = cv2.VideoCapture(video_file_path)
    video_fps = video.get(cv2.CAP_PROP_FPS)
    frame_interval = int(round(video_fps / fps))
    output_dir = Path(video_file_path).parent.joinpath("extractedFrames")
    output_dir.mkdir(exist_ok=True)
    
    count = 0
    saved_frame_count = 0
    while True:
        ret, frame = video.read()
        if not ret:
            break
        if count % frame_interval == 0:
            frame_file = output_dir / f"frame_{saved_frame_count:04d}.png"
            cv2.imwrite(str(frame_file), frame)
            saved_frame_count += 1
        count += 1

    video.release()
    print(f"Extracted {saved_frame_count} frames to {output_dir}")

def main():
    parser = argparse.ArgumentParser(description="Extract frames from a video at specified FPS.")
    parser.add_argument("video_file_path", type=str, help="Path to the video file.")
    parser.add_argument("--fps", type=float, default=1.0, help="Frames per second to extract.")
    args = parser.parse_args()

    create_frames(args.video_file_path, args.fps)

if __name__ == "__main__":
    main()
