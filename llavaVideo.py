
import subprocess
import os

def call_llava_cli(image_path, prompt):
        command = [
            "python", "-m", "llava.serve.cli",
            "--model-path", "liuhaotian/llava-v1.5-7b",
            "--image-file", image_path,
            "--load-4bit"
            # Add other necessary arguments here
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        return result.stdout

def process_images(image_directory, prompt):
    responses = []
    for image_file in os.listdir(image_directory):
        if image_file.endswith(".jpg"):  # Assuming JPEG images
            image_path = os.path.join(image_directory, image_file)
            response = call_llava_cli(image_path, prompt)
            print(f"Response for {image_file}: {response}")
            responses.append(response)
    return responses

# Example usage
image_dir = "/workspace/video-tools/testing_img"
prompt = "Describe this scene"  # Your specific prompt
results = process_images(image_dir, prompt)

# Process results as needed
for result in results:
    print(result)

