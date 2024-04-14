import argparse
from pydub import AudioSegment
import os

def get_file_size_in_mb(file_path):
    """ Get file size in megabytes """
    return os.path.getsize(file_path) / (1024 * 1024)

def calculate_bitrate(current_size, target_size, duration_seconds):
    """
    Calculate the bitrate required to achieve the target size.
    Formula: Target Bitrate = (Target Size * 8) / Duration in seconds
    """
    target_bitrate = (target_size * 8) / duration_seconds
    return max(int(target_bitrate), 8)  # Ensure bitrate doesn't go below 8 kbps

def compress_audio(input_file_path, target_size_mb, output_format="mp3"):
    """ Compress the audio file to a specific size """

    # Load the audio file
    audio = AudioSegment.from_file(input_file_path)

    # Get current file size and duration
    current_size_mb = get_file_size_in_mb(input_file_path)
    duration_seconds = len(audio) / 1000.0

    # If the file is already smaller than the target size, no compression needed
    if current_size_mb <= target_size_mb:
        print("The file is already smaller than the target size. No compression needed.")
        return input_file_path

    # Calculate the required bitrate
    target_bitrate = calculate_bitrate(current_size_mb, target_size_mb, duration_seconds)

    # Compress and export the file
    file_dir, file_name = os.path.split(input_file_path)
    output_file_name = os.path.splitext(file_name)[0] + "_compressed." + output_format
    output_file_path = os.path.join(file_dir, output_file_name)
    audio.export(output_file_path, format=output_format, bitrate=f"{target_bitrate}k")

    return output_file_path

def main():
    parser = argparse.ArgumentParser(description="Compress an audio file to a specified size.")
    parser.add_argument('file_path', type=str, help="Path to the audio file to be compressed")
    parser.add_argument('--target_size', type=float, default=50, help="Target size of the file in MB (default: 50 MB)")
    args = parser.parse_args()

    compressed_file = compress_audio(args.file_path, args.target_size)
    print(f"Compressed file saved as: {compressed_file}")

if __name__ == "__main__":
    main()
