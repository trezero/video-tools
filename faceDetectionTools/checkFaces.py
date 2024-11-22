#!/usr/bin/env python3

import os
import sys
import json
import csv
from pathlib import Path
from PIL import Image
from datetime import datetime
import argparse
from tqdm import tqdm
import ollama
import signal
import time
import psutil
from contextlib import contextmanager

class Config:
    """Configuration class to hold all settings"""
    def __init__(self):
        self.MAX_IMAGE_SIZE = (1024, 1024)
        self.BATCH_SIZE = 5
        self.TIMEOUT_SECONDS = 30
        self.MEMORY_THRESHOLD = 90  # Percentage
        self.MODEL_NAME = "llama3.2-vision:latest"

# Global configuration object
config = Config()

@contextmanager
def timeout(seconds):
    """Context manager for timing out operations"""
    def signal_handler(signum, frame):
        raise TimeoutError("Request timed out")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

def check_system_resources():
    """Check system resources before processing"""
    try:
        # Check available memory
        memory = psutil.virtual_memory()
        if memory.percent > config.MEMORY_THRESHOLD:
            print(f"Warning: System memory usage is at {memory.percent}%!")
            return False
            
        # Check GPU memory if possible
        try:
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            gpu_usage = (info.used / info.total) * 100
            if gpu_usage > config.MEMORY_THRESHOLD:
                print(f"Warning: GPU memory usage is at {gpu_usage:.1f}%!")
                return False
            print(f"GPU Memory - Used: {info.used/1024**3:.1f}GB, Free: {info.free/1024**3:.1f}GB, Total: {info.total/1024**3:.1f}GB")
        except Exception as e:
            print(f"Note: Unable to check GPU memory: {str(e)}")
            
        return True
    except Exception as e:
        print(f"Warning: Error checking system resources: {str(e)}")
        return True  # Continue if resource check fails

def is_valid_image_file(filepath):
    """Check if the file is a valid image file we should process."""
    # Skip hidden files and system files
    filename = os.path.basename(filepath)
    if filename.startswith('.') or filename.startswith('._'):
        return False
        
    # Check file extension
    valid_extensions = {'.png', '.jpg', '.jpeg', '.webp'}
    file_extension = os.path.splitext(filename)[1].lower()
    if file_extension not in valid_extensions:
        return False
        
    # Try to verify it's a valid image file
    try:
        with Image.open(filepath) as img:
            img.verify()
        return True
    except Exception:
        return False

def check_ollama_status():
    """Check if Ollama is running and properly initialized."""
    try:
        print("Checking Ollama status...")
        with timeout(10):  # 10 second timeout for status check
            models = ollama.list()
            print(f"Available models: {models}")
            
            # Check if our required model is available
            model_available = any(model.model == config.MODEL_NAME for model in models.models)
            if not model_available:
                print(f"Warning: {config.MODEL_NAME} not found in available models!")
                return False
            return True
    except TimeoutError:
        print("Error: Ollama status check timed out")
        return False
    except Exception as e:
        print(f"Error connecting to Ollama: {str(e)}")
        return False

def get_image_info(image_path):
    """Get image dimensions and file size."""
    try:
        with Image.open(image_path) as img:
            dimensions = img.size
        file_size = os.path.getsize(image_path) / 1024  # Convert to KB
        return dimensions, file_size
    except Exception as e:
        print(f"Error getting image info: {str(e)}")
        return None, None

def extract_json_from_text(text):
    """Extract JSON from text that might contain other content."""
    try:
        # First try to parse the entire text as JSON
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON-like content within the text
        try:
            # Look for content between curly braces
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = text[start:end]
                return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # If no valid JSON found, create a structured response from the text
        return {
            "suitable": "No" if any(negative in text.lower() for negative in ["blur", "dark", "occlu", "poor", "low"]) else "Yes",
            "explanation": text.strip(),
            "quality_score": 1  # Default quality score when we have to parse non-JSON response
        }

def check_face_quality(image_path):
    """Send image to Ollama vision model and get quality assessment."""
    start_time = time.time()
    dimensions = None
    file_size = None
    
    try:
        print(f"\nProcessing image: {image_path}")
        dimensions, file_size = get_image_info(image_path)
        
        prompt = """You are a VERY strict face quality assessment expert. Your job is to be extremely critical and selective.
Your primary goal is to find issues with facial images for AI training. Be harsh in your assessment - only the absolute best images should pass.

STRICT REQUIREMENTS for a "Yes":
1. Face MUST be clearly facing the camera (frontal view)
2. BOTH eyes must be clearly visible
3. NO occlusions (hats, sunglasses, masks, hands, etc.)
4. Face must be well-lit and in sharp focus
5. Neutral or natural expression preferred
6. High enough resolution
7. No extreme shadows or backlighting

AUTOMATIC REJECTION if any of these are present:
- Profile or side view
- Single eye visible
- Face partially covered
- Blurry or low resolution
- Extreme expressions
- Heavy shadows or poor lighting
- Any occlusions (hats, glasses, etc.)

QUALITY SCORE (1-10):
10: Perfect training image - frontal, clear, well-lit, no issues
9: Excellent - very minor imperfections
8: Good - slight angle or lighting issues
7: Usable - noticeable but acceptable issues
1-6: Not suitable for training - multiple issues

You must respond in this exact JSON format:
{
    "suitable": "Yes/No",
    "explanation": "List key issues or qualities",
    "quality_score": X
}

Requirements:
- "suitable" must be exactly "Yes" or "No" (be very strict, reject if in doubt)
- "explanation" should be a single line of specific issues or qualities
- "quality_score" must be 1-10 (only 7+ should be marked as suitable)

Example responses:
{
    "suitable": "Yes",
    "explanation": "perfect frontal view, both eyes clear, well-lit, sharp, no occlusions",
    "quality_score": 10
}

{
    "suitable": "No",
    "explanation": "side angle, right eye not visible, wearing cap",
    "quality_score": 3
}

{
    "suitable": "No",
    "explanation": "blurry, shadows on face, looking down",
    "quality_score": 2
}

Remember: Your job is to be extremely critical. When in doubt, reject the image. We only want the absolute best quality images for training."""

        try:
            print("Sending request to Ollama...")  # Debug log
            with timeout(config.TIMEOUT_SECONDS):
                response = ollama.chat(
                    model=config.MODEL_NAME,
                    messages=[{
                        'role': 'user',
                        'content': prompt,
                        'images': [image_path]
                    }]
                )
                print("Received response from Ollama")  # Debug log
                print(f"Raw response: {response}")  # Debug log
                
            try:
                content = response['message']['content']
                print(f"Attempting to parse response content: {content}")  # Debug log
                
                # Use the new JSON extraction function
                assessment = extract_json_from_text(content)
                print(f"Successfully parsed response: {assessment}")  # Debug log
                
                # Validate and clean up the response
                if not isinstance(assessment.get('suitable'), str):
                    assessment['suitable'] = str(assessment.get('suitable', 'Error'))
                if not isinstance(assessment.get('quality_score'), (int, float)):
                    assessment['quality_score'] = 1
                
                # Add additional metrics
                processing_time = time.time() - start_time
                assessment['processing_time'] = round(processing_time, 2)
                if dimensions:
                    assessment['width'] = dimensions[0]
                    assessment['height'] = dimensions[1]
                if file_size:
                    assessment['file_size_kb'] = round(file_size, 2)
                
                return assessment
                
            except Exception as e:
                print(f"Error parsing response: {str(e)}")  # Debug log
                return {
                    "suitable": "Error",
                    "explanation": f"Error parsing model response: {str(e)}",
                    "quality_score": 1,
                    "processing_time": round(time.time() - start_time, 2),
                    "width": dimensions[0] if dimensions else None,
                    "height": dimensions[1] if dimensions else None,
                    "file_size_kb": round(file_size, 2) if file_size else None
                }
            
        except TimeoutError:
            print("Request timed out")  # Debug log
            return {
                "suitable": "Error",
                "explanation": f"Request timed out after {config.TIMEOUT_SECONDS} seconds",
                "quality_score": 1,
                "processing_time": round(time.time() - start_time, 2),
                "width": dimensions[0] if dimensions else None,
                "height": dimensions[1] if dimensions else None,
                "file_size_kb": round(file_size, 2) if file_size else None
            }
        except Exception as e:
            print(f"Error during Ollama API call: {str(e)}")  # Debug log
            return {
                "suitable": "Error",
                "explanation": f"Error calling Ollama API: {str(e)}",
                "quality_score": 1,
                "processing_time": round(time.time() - start_time, 2),
                "width": dimensions[0] if dimensions else None,
                "height": dimensions[1] if dimensions else None,
                "file_size_kb": round(file_size, 2) if file_size else None
            }
            
    except Exception as e:
        print(f"Unexpected error: {str(e)}")  # Debug log
        return {
            "suitable": "Error",
            "explanation": f"Error processing image: {str(e)}",
            "quality_score": 1,
            "processing_time": round(time.time() - start_time, 2),
            "width": dimensions[0] if dimensions else None,
            "height": dimensions[1] if dimensions else None,
            "file_size_kb": round(file_size, 2) if file_size else None
        }

def process_face_directory(input_dir, debug=False):
    """Process all face images in the input directory and its subdirectories."""
    if not os.path.exists(input_dir):
        print(f"Error: Directory {input_dir} does not exist!")
        return

    # Check Ollama status first
    if not check_ollama_status():
        print("Error: Unable to connect to Ollama or required model not available.")
        return

    print(f"Processing images in: {input_dir}")
    
    # Get all image files
    image_files = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            filepath = os.path.join(root, file)
            if is_valid_image_file(filepath):
                image_files.append(filepath)

    if not image_files:
        print("No valid image files found in the directory!")
        return

    # In debug mode, only process the first image
    if debug:
        print(f"Debug mode: Processing only the first image")
        image_files = image_files[:1]

    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), "faceRatings")
    os.makedirs(output_dir, exist_ok=True)

    # Create CSV file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = os.path.join(output_dir, f"face_quality_results_{timestamp}.csv")
    
    with open(csv_filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Folder', 'Image', 'Quality', 'Explanation', 'Score', 'Width', 'Height', 'File_Size_KB', 'Processing_Time_Sec'])
        
        # Process images in batches
        for i in range(0, len(image_files), config.BATCH_SIZE):
            batch = image_files[i:i + config.BATCH_SIZE]
            
            # Check system resources before each batch
            if not check_system_resources():
                print("Pausing for 30 seconds to allow resources to free up...")
                time.sleep(30)
                if not check_system_resources():
                    print("Warning: System resources still constrained, but continuing...")
            
            for image_path in tqdm(batch, desc=f"Processing batch {i//config.BATCH_SIZE + 1}"):
                result = check_face_quality(image_path)
                
                # Get parent folder name
                folder_name = os.path.basename(os.path.dirname(image_path))
                
                csvwriter.writerow([
                    folder_name,
                    os.path.basename(image_path),
                    result.get('suitable', 'Error'),
                    result.get('explanation', 'Unknown error'),
                    result.get('quality_score', 1),
                    result.get('width', ''),
                    result.get('height', ''),
                    result.get('file_size_kb', ''),
                    result.get('processing_time', '')
                ])
                csvfile.flush()  # Ensure each result is written immediately
                
                if debug:
                    print(f"\nDebug: Result for {os.path.basename(image_path)}:")
                    print(f"Folder: {folder_name}")
                    print(f"Quality: {result.get('suitable', 'Error')}")
                    print(f"Explanation: {result.get('explanation', 'Unknown error')}")
                    print(f"Score: {result.get('quality_score', 1)}/10")
                    print(f"Dimensions: {result.get('width', '')}x{result.get('height', '')}")
                    print(f"File Size: {result.get('file_size_kb', '')} KB")
                    print(f"Processing Time: {result.get('processing_time', '')} sec")
                
                # Add a small delay between images to prevent overwhelming the system
                time.sleep(1)

    print(f"\nResults saved to: {csv_filename}")

def main():
    parser = argparse.ArgumentParser(description='Process face images for quality assessment.')
    parser.add_argument('input_dir', help='Directory containing face images')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode (process single image)')
    parser.add_argument('--batch-size', type=int, default=config.BATCH_SIZE, 
                      help=f'Number of images to process in each batch (default: {config.BATCH_SIZE})')
    args = parser.parse_args()
    
    # Update batch size from command line argument
    config.BATCH_SIZE = args.batch_size
    
    process_face_directory(args.input_dir, args.debug)

if __name__ == "__main__":
    main()