import cv2
import numpy as np
from pathlib import Path
import argparse
import time
from collections import defaultdict
import tensorflow as tf
from mtcnn import MTCNN
from typing import NamedTuple
import subprocess
import os

# ... [Previous GPU check and environment setup code remains the same] ...

class FaceOccurrence(NamedTuple):
    frame_num: int
    image: np.ndarray

def extract_faces(video_path: str, output_folder: str, max_faces: int = 30, images_per_face: int = 30, 
                  batch_size: int = 4, frames_per_second: float = 1.0) -> None:
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return

    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(video.get(cv2.CAP_PROP_FPS))
    duration = total_frames / fps

    print(f"Processing video: {video_path}")
    print(f"Total frames: {total_frames}")
    print(f"Video FPS: {fps}")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Sampling at {frames_per_second} frame(s) per second")

    face_occurrences: dict[int, list[FaceOccurrence]] = defaultdict(list)
    face_count = 0
    processed_frames = 0
    start_time = time.time()

    # Initialize MTCNN detector
    detector = MTCNN()

    # Calculate frame interval based on desired frames per second
    frame_interval = max(1, int(fps / frames_per_second))

    print("First pass: Identifying unique faces...")
    while True:
        frames = []
        frame_numbers = []
        for _ in range(batch_size):
            # Skip frames to achieve desired sampling rate
            for _ in range(frame_interval):
                ret, frame = video.read()
                if not ret:
                    break
                processed_frames += 1
            if not ret:
                break
            frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            frame_numbers.append(processed_frames)

        if not frames:
            break

        if processed_frames % 100 == 0:
            progress = (processed_frames / total_frames) * 100
            print(f"Progress: {progress:.2f}%")

        # Detect faces in batch
        batch_faces = detector.detect_faces(np.array(frames))

        for i, faces in enumerate(batch_faces):
            for face in faces:
                x, y, w, h = face['box']
                face_img = frames[i][y:y+h, x:x+w]
                
                # Simple face comparison using mean pixel difference
                new_face = True
                for existing_face_id, occurrences in face_occurrences.items():
                    if occurrences:
                        existing_face = cv2.resize(occurrences[0].image, (100, 100))
                        current_face = cv2.resize(face_img, (100, 100))
                        diff = np.mean(np.abs(existing_face - current_face))
                        if diff < 50:  # Adjust this threshold as needed
                            new_face = False
                            face_occurrences[existing_face_id].append(FaceOccurrence(frame_numbers[i], face_img))
                            break

                if new_face and face_count < max_faces:
                    face_count += 1
                    face_occurrences[face_count].append(FaceOccurrence(frame_numbers[i], face_img))
                    print(f"New face detected! Total unique faces: {face_count}")

    video.release()
    print(f"First pass complete. {face_count} unique faces found.")

    print("Second pass: Extracting distributed samples for each face...")
    for face_id, occurrences in face_occurrences.items():
        face_folder = output_path / f"face{face_id:02d}"
        face_folder.mkdir(exist_ok=True)

        total_occurrences = len(occurrences)
        if total_occurrences <= images_per_face:
            samples = occurrences
        else:
            step = total_occurrences // images_per_face
            samples = occurrences[::step][:images_per_face]

        for i, occurrence in enumerate(samples):
            cv2.imwrite(str(face_folder / f"image{i:02d}_frame{occurrence.frame_num}.jpg"), cv2.cvtColor(occurrence.image, cv2.COLOR_RGB2BGR))

        print(f"Saved {len(samples)} images for face {face_id}")

    print(f"Face extraction complete. Results saved in the '{output_folder}' folder.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract face images from a video file.")
    parser.add_argument("video_path", help="Path to the input video file")
    parser.add_argument("--output", default="foundFaces", help="Output folder name")
    parser.add_argument("--max_faces", type=int, default=30, help="Maximum number of unique faces to extract")
    parser.add_argument("--images_per_face", type=int, default=30, help="Number of images to extract per face")
    parser.add_argument("--batch_size", type=int, default=4, help="Number of frames to process in each batch")
    parser.add_argument("--frames_per_second", type=float, default=1.0, help="Number of frames to sample per second")
    args = parser.parse_args()

    try:
        extract_faces(args.video_path, args.output, args.max_faces, args.images_per_face, args.batch_size, args.frames_per_second)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()