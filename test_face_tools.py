import cv2
import numpy as np
from pathlib import Path
from faceDetectionTools import FaceQualityAnalyzer, extract_faces

def test_face_quality_analyzer():
    print("Testing FaceQualityAnalyzer initialization...")
    try:
        # Initialize the analyzer
        analyzer = FaceQualityAnalyzer()
        print("✓ Successfully initialized FaceQualityAnalyzer")
        
        # Create a simple test image (gray square)
        test_image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        
        # Test quality analysis
        print("\nTesting face quality analysis...")
        score, metrics = analyzer.get_face_quality_score(test_image)
        print("✓ Successfully ran quality analysis")
        print(f"Quality score: {score}")
        print("Quality metrics:", metrics)
        
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def main():
    print("Running face detection tools tests...\n")
    
    # Check if required model file exists
    model_path = Path("faceDetectionTools/shape_predictor_68_face_landmarks.dat")
    if not model_path.exists():
        print(f"✗ Error: Required model file not found at {model_path}")
        return
    
    # Run tests
    tests_passed = []
    tests_passed.append(test_face_quality_analyzer())
    
    # Print summary
    print("\nTest Summary:")
    print(f"Tests passed: {sum(tests_passed)}/{len(tests_passed)}")
    print(f"Tests failed: {len(tests_passed) - sum(tests_passed)}/{len(tests_passed)}")

if __name__ == "__main__":
    main()
