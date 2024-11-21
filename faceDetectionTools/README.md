# Face Detection Tools

A comprehensive Python package for high-quality face detection, extraction, and quality analysis from videos and images. This package provides GPU-accelerated face detection, advanced face quality metrics, and intelligent face selection algorithms.

## Features

### 1. Face Quality Analysis (`face_quality.py`)
- Comprehensive face quality metrics:
  - Blur detection (Laplacian and FFT methods)
  - Face alignment analysis
  - Face orientation detection (yaw, pitch, roll)
  - Eye openness detection
  - Brightness and contrast checking
  - Resolution assessment
- Configurable quality thresholds
- Detailed quality metrics output

### 2. Training Face Generation (`generateTrainingFaces.py`)
- GPU-accelerated face detection using MTCNN
- Intelligent face selection with quality filtering
- Multiprocessing support for parallel processing
- Advanced face tracking and uniqueness detection
- Progress tracking with ETA estimation
- Configurable sampling rates and batch sizes

## Installation

### Prerequisites
```bash
# Install required packages
pip install -r requirements.txt

# Download the shape predictor model
wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
bunzip2 shape_predictor_68_face_landmarks.dat.bz2
```

### Dependencies
- tensorflow>=2.6.0
- mtcnn>=0.1.1
- dlib>=19.22.0
- opencv-python>=4.5.0
- numpy>=1.21.0
- face-recognition>=1.3.0
- scipy>=1.7.0
- tqdm>=4.62.0

## Usage

### Face Quality Analysis
```python
from faceDetectionTools import FaceQualityAnalyzer

# Initialize the analyzer
analyzer = FaceQualityAnalyzer()

# Analyze face quality
quality_score, metrics = analyzer.get_face_quality_score(face_image)

# Access detailed metrics
print(f"Quality Score: {quality_score}")
print("Detailed Metrics:", metrics)
```

### Training Face Generation
```python
from faceDetectionTools import extract_faces

# Extract faces from a video
extract_faces(
    video_path="path/to/video.mp4",
    output_folder="output_faces",
    max_faces=30,              # Maximum number of unique faces to extract
    images_per_face=30,        # Number of images per unique face
    batch_size=4,              # GPU batch size
    frames_per_second=1.0      # Sampling rate
)
```

## Quality Metrics

The face quality analyzer provides the following metrics:

1. **Blur Score** (0-1)
   - Uses both Laplacian variance and FFT analysis
   - Higher score indicates sharper image

2. **Alignment Score** (0-1)
   - Measures face alignment based on eye positions
   - Perfect alignment = 1.0

3. **Orientation Scores**
   - Yaw (horizontal rotation)
   - Pitch (vertical rotation)
   - Roll (tilt)
   - Each ranges from 0-1, where 1 = frontal

4. **Eye Openness** (0-1)
   - Based on Eye Aspect Ratio (EAR)
   - Higher score indicates more open eyes

5. **Brightness & Contrast** (0-1)
   - Optimal brightness around 128/255
   - Higher contrast scores indicate better detail

## Performance Optimization

### GPU Acceleration
- Automatically detects and configures available GPUs
- Dynamic batch size adjustment based on GPU memory
- Configurable memory growth settings

### Parallel Processing
- Multiprocessing for face detection
- Thread pooling for I/O operations
- Efficient frame extraction and processing

## Error Handling

The package includes comprehensive error handling:
- Input validation for video files
- GPU memory management
- Progress tracking and ETA estimation
- Detailed error messages and logging

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:
- Bug fixes
- Feature enhancements
- Documentation improvements
- Performance optimizations

## License

This project is licensed under the MIT License - see the LICENSE file for details.
