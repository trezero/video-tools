import cv2
import os
import sys

# Configuration: Number of images to extract per minute
IMAGES_PER_MINUTE = 10

def extract_images(video_path, images_per_minute):
    # Create the output directory
    video_name = os.path.basename(video_path).split('.')[0]
    output_dir = f"{video_name}_images"
    os.makedirs(output_dir, exist_ok=True)

    # Open the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_minutes = total_frames / (fps * 60)
    frames_to_extract = int(duration_minutes * images_per_minute)

    # Calculate the frame interval
    frame_interval = total_frames // frames_to_extract

    frame_count = 0
    extracted_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            output_path = os.path.join(output_dir, f"frame_{extracted_count:04d}.jpg")
            cv2.imwrite(output_path, frame)
            extracted_count += 1

        frame_count += 1

    cap.release()
    print(f"Extracted {extracted_count} images to {output_dir}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extractImagesFromVid.py <video_file_path>")
        sys.exit(1)

    video_path = sys.argv[1]
    extract_images(video_path, IMAGES_PER_MINUTE)
