import cv2
import sys

video_file = sys.argv[1] 

cap = cv2.VideoCapture(video_file)

frame_count = 0
success = True

while success and frame_count < 10:
    success, frame = cap.read()
    if success:
        cv2.imwrite(f"frame{frame_count}.jpg", frame)
        frame_count += 1

cap.release()