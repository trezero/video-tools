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

The face extraction tool now supports configuration-based usage for better flexibility and reproducibility.

#### Basic Usage

1. Using default configuration:
```bash
python generateTrainingFaces.py video.mp4
```

2. Using custom configuration:
```bash
python generateTrainingFaces.py video.mp4 --config custom_config.json
```

#### Configuration File

The tool uses a JSON configuration file (`faceGenConfig.json`) to control all aspects of face extraction. Here's the default configuration structure:

```json
{
    "output_dir": "extracted_faces",
    "max_faces": 30,
    "images_per_face": 30,
    "min_face_size": 40,
    "min_confidence": 0.95,
    "min_quality": 0.6,
    "batch_size": 4,
    "fps": 1.0,
    "use_gpu": true,
    "gpu_memory_fraction": 0.7,
    "face_similarity_threshold": 0.6,
    "skip_existing": true,
    "save_metadata": true,
    "quality_metrics": {
        "blur_threshold": 100,
        "brightness_range": [0.2, 0.8],
        "min_face_angle": 30,
        "min_eye_openness": 0.3
    },
    "logging": {
        "level": "INFO",
        "show_progress": true
    }
}
```

#### Configuration Parameters

1. **Basic Settings**
   - `output_dir`: Directory where extracted faces will be saved
   - `max_faces`: Maximum number of unique faces to extract
   - `images_per_face`: Number of images to save per unique face
   - `fps`: Frames per second to process from video

2. **Face Detection Settings**
   - `min_face_size`: Minimum face size in pixels
   - `min_confidence`: Minimum confidence score for face detection
   - `min_quality`: Minimum quality score for face selection
   - `face_similarity_threshold`: Threshold for determining unique faces

3. **Performance Settings**
   - `use_gpu`: Enable/disable GPU acceleration
   - `gpu_memory_fraction`: Fraction of GPU memory to use
   - `batch_size`: Batch size for processing

4. **Quality Metrics**
   - `blur_threshold`: Threshold for blur detection
   - `brightness_range`: Acceptable brightness range [min, max]
   - `min_face_angle`: Minimum acceptable face angle
   - `min_eye_openness`: Minimum eye aspect ratio

5. **Output Settings**
   - `skip_existing`: Skip processing if output directory exists
   - `save_metadata`: Save detailed metadata for each face

#### Output Structure

The tool creates the following directory structure:
```
output_dir/
├── face_1/
│   ├── frame_0001_quality_0.85.jpg
│   ├── frame_0015_quality_0.92.jpg
│   └── metadata.json
├── face_2/
│   ├── frame_0008_quality_0.88.jpg
│   ├── frame_0023_quality_0.90.jpg
│   └── metadata.json
└── extraction_stats.json
```

Each face directory contains:
- High-quality face images named with frame number and quality score
- `metadata.json` with detailed face metrics and extraction information
- Global `extraction_stats.json` with overall processing statistics

#### Custom Configuration Example

Create a custom configuration for high-quality face extraction:

```json
{
    "output_dir": "high_quality_faces",
    "max_faces": 50,
    "images_per_face": 50,
    "min_face_size": 60,
    "min_confidence": 0.98,
    "min_quality": 0.8,
    "batch_size": 8,
    "fps": 2.0,
    "quality_metrics": {
        "blur_threshold": 150,
        "brightness_range": [0.3, 0.7],
        "min_face_angle": 20,
        "min_eye_openness": 0.4
    }
}
```

This configuration will:
- Extract more faces with higher quality requirements
- Process frames at 2 FPS for more temporal coverage
- Use stricter quality metrics for better results
- Output to a custom directory

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
