import cv2
import numpy as np
from pathlib import Path
import argparse
import time
from collections import defaultdict
import tensorflow as tf
import face_recognition
from typing import NamedTuple

# Ensure TensorFlow is using the GPU
physical_devices = tf.config.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)
    print("GPU is available and will be used.")
else:
    print("No GPU found. Using CPU.")

class FaceOccurrence(NamedTuple):
    frame_num: int
    image: np.ndarray

def extract_faces(video_path: str, output_folder: str, max_faces: int = 30, images_per_face: int = 30) -> None:
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
    print(f"Duration: {duration:.2f} seconds")

    face_occurrences: dict[int, list[FaceOccurrence]] = defaultdict(list)
    face_encodings: list[np.ndarray] = []
    face_count = 0
    processed_frames = 0
    start_time = time.time()

    print("First pass: Identifying unique faces...")
    while True:
        ret, frame = video.read()
        if not ret:
            break

        processed_frames += 1
        if processed_frames % 100 == 0:
            progress = (processed_frames / total_frames) * 100
            print(f"Progress: {progress:.2f}%")

        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Find all face locations and face encodings in the current frame
        face_locations = face_recognition.face_locations(rgb_frame)
        current_face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_location, face_encoding in zip(face_locations, current_face_encodings):
            top, right, bottom, left = face_location
            face_img = frame[top:bottom, left:right]
            
            if len(face_encodings) == 0:
                face_count += 1
                face_encodings.append(face_encoding)
                face_occurrences[face_count].append(FaceOccurrence(processed_frames, face_img))
                print(f"New face detected! Total unique faces: {face_count}")
            else:
                # Compare face encodings
                matches = face_recognition.compare_faces(face_encodings, face_encoding)
                if True in matches:
                    matched_face_idx = matches.index(True)
                    face_occurrences[matched_face_idx + 1].append(FaceOccurrence(processed_frames, face_img))
                elif face_count < max_faces:
                    face_count += 1
                    face_encodings.append(face_encoding)
                    face_occurrences[face_count].append(FaceOccurrence(processed_frames, face_img))
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
            cv2.imwrite(str(face_folder / f"image{i:02d}_frame{occurrence.frame_num}.jpg"), occurrence.image)

        print(f"Saved {len(samples)} images for face {face_id}")

    print(f"Face extraction complete. Results saved in the '{output_folder}' folder.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract face images from a video file.")
    parser.add_argument("video_path", help="Path to the input video file")
    parser.add_argument("--output", default="foundFaces", help="Output folder name")
    parser.add_argument("--max_faces", type=int, default=30, help="Maximum number of unique faces to extract")
    parser.add_argument("--images_per_face", type=int, default=30, help="Number of images to extract per face")
    args = parser.parse_args()

    try:
        extract_faces(args.video_path, args.output, args.max_faces, args.images_per_face)
    except Exception as e:
        print(f"An error occurred: {str(e)}")