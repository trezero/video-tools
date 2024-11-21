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
import face_recognition
from scipy.spatial.distance import cosine
import multiprocessing
from .face_quality import FaceQualityAnalyzer

class FaceOccurrence(NamedTuple):
    frame_num: int
    image: np.ndarray
    quality_score: float
    quality_metrics: dict
    embedding: np.ndarray

def get_face_quality(face_img, quality_analyzer):
    """Get comprehensive face quality score and metrics"""
    score, metrics = quality_analyzer.get_face_quality_score(face_img)
    return score, metrics

def extract_faces(video_path: str, output_folder: str, max_faces: int = 30, images_per_face: int = 30, 
                 batch_size: int = 4, frames_per_second: float = 1.0) -> None:
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    # Set up GPU configuration
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            print(f"GPU acceleration enabled. Found {len(gpus)} GPU(s)")
        except RuntimeError as e:
            print(f"GPU configuration failed: {e}")
    else:
        print("No GPU found. Using CPU only.")

    # Initialize face quality analyzer
    quality_analyzer = FaceQualityAnalyzer()

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

    # Initialize MTCNN detector with larger min_face_size for better detection
    detector = MTCNN(min_face_size=40)

    # Initialize face recognition model
    known_face_encodings = []
    known_face_ids = []

    # Calculate frame interval based on desired frames per second
    frame_interval = max(1, int(fps / frames_per_second))

    # Determine optimal batch size based on available GPU memory
    if gpus:
        try:
            gpu = tf.config.experimental.get_visible_devices('GPU')[0]
            gpu_memory = tf.config.experimental.get_memory_info(gpu)['free']
            batch_size = min(batch_size, max(1, int(gpu_memory / (1024 * 1024 * 100))))  # Adjust based on GPU memory
            print(f"Adjusted batch size to {batch_size} based on available GPU memory")
        except:
            pass

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
            elapsed_time = time.time() - start_time
            eta = (elapsed_time / processed_frames) * (total_frames - processed_frames)
            print(f"Progress: {progress:.2f}% (ETA: {eta:.2f}s)")

        # Process frames in parallel using multiprocessing for face detection
        with multiprocessing.Pool() as pool:
            batch_faces = pool.map(detector.detect_faces, frames)

        for i, faces in enumerate(batch_faces):
            for face in faces:
                x, y, w, h = face['box']
                confidence = face['confidence']
                
                # Skip low confidence detections
                if confidence < 0.95:
                    continue
                    
                face_img = frames[i][y:y+h, x:x+w]
                
                # Check face quality with comprehensive metrics
                quality_score, quality_metrics = get_face_quality(face_img, quality_analyzer)
                if quality_score < 0.6:  # Increased quality threshold
                    continue
                
                # Get face embedding
                try:
                    face_encoding = face_recognition.face_encodings(face_img)[0]
                except IndexError:
                    continue
                
                # Compare with existing faces
                new_face = True
                if known_face_encodings:
                    # Compare face distances
                    face_distances = [cosine(face_encoding, enc) for enc in known_face_encodings]
                    min_distance = min(face_distances)
                    if min_distance < 0.6:  # Threshold for face similarity
                        face_id = known_face_ids[face_distances.index(min_distance)]
                        new_face = False
                        face_occurrences[face_id].append(
                            FaceOccurrence(frame_numbers[i], face_img, quality_score, quality_metrics, face_encoding)
                        )
                
                if new_face and face_count < max_faces:
                    face_count += 1
                    known_face_encodings.append(face_encoding)
                    known_face_ids.append(face_count)
                    face_occurrences[face_count].append(
                        FaceOccurrence(frame_numbers[i], face_img, quality_score, quality_metrics, face_encoding)
                    )
                    print(f"New face detected! Total unique faces: {face_count}")

    video.release()
    print(f"First pass complete. {face_count} unique faces found.")

    print("Second pass: Extracting distributed samples for each face...")
    for face_id, occurrences in face_occurrences.items():
        face_folder = output_path / f"face{face_id:02d}"
        face_folder.mkdir(exist_ok=True)
        
        # Sort occurrences by quality score
        occurrences.sort(key=lambda x: x.quality_score, reverse=True)
        
        # Save quality metrics for the best sample
        best_metrics = occurrences[0].quality_metrics
        with open(face_folder / "quality_metrics.txt", "w") as f:
            for metric, value in best_metrics.items():
                f.write(f"{metric}: {value}\n")
        
        # Select best quality samples with good distribution
        if len(occurrences) <= images_per_face:
            samples = occurrences
        else:
            # Divide occurrences into segments and take the best quality frame from each segment
            segment_size = len(occurrences) // images_per_face
            samples = []
            for i in range(0, len(occurrences), segment_size):
                segment = occurrences[i:i + segment_size]
                samples.append(max(segment, key=lambda x: x.quality_score))
            samples = samples[:images_per_face]

        # Save selected samples
        for i, sample in enumerate(samples):
            output_file = face_folder / f"frame_{sample.frame_num:04d}_quality_{sample.quality_score:.2f}.jpg"
            cv2.imwrite(str(output_file), cv2.cvtColor(sample.image, cv2.COLOR_RGB2BGR))

    print(f"Processing complete! Found {face_count} unique faces.")
    print(f"Results saved to: {output_path}")
    print(f"Total processing time: {time.time() - start_time:.2f} seconds")

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