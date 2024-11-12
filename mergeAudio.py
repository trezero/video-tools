import os
import sys
from pydub import AudioSegment
from pydub.silence import split_on_silence

def concatenate_audios(folder_path, file_extension, silence_thresh=-40, silence_duration=1000):
    # silence_thresh is the silence threshold in dB
    # silence_duration is the maximum length of silence allowed (in milliseconds)

    # Check for valid file extension
    if file_extension not in ['wav', 'mp3']:
        print("Unsupported file extension. Please choose wav or mp3")
        return

    # Collect all files in the directory with the specified extension
    files = sorted([f for f in os.listdir(folder_path) if f.endswith(file_extension)])
    if not files:
        print("No audio files found in the directory with extension", file_extension)
        return

    final_clip = AudioSegment.empty()
    for f in files:
        file_path = os.path.join(folder_path, f)
        print(f"Processing file: {file_path}")  # This line prints each file name
        try:
            clip = AudioSegment.from_file(file_path)

            # Split clip where silence is 1 second or longer and reduce that silence
            chunks = split_on_silence(
                clip,
                min_silence_len=silence_duration,
                silence_thresh=silence_thresh
            )

            # Reduce silence to 1 second between chunks
            chunk_length = 0
            for chunk in chunks:
                chunk_length += len(chunk)
                final_clip += chunk + AudioSegment.silent(duration=1000)  # Add only 1 second of silence

            print(f"Total non-silent chunk length: {chunk_length}ms")

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
    
    # Output file
    if len(final_clip):
        output_file = os.path.join(folder_path, f"final_output.{file_extension}")
        final_clip.export(output_file, format=file_extension)
        print(f"Concatenated audio has been saved to {output_file}")
    else:
        print("No audio clips to concatenate.")

if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python concatenate_audio.py <folder_path> <file_extension> [silence_threshold]")
        sys.exit(1)

    folder = sys.argv[1]
    extension = sys.argv[2].strip('.')  # Remove the dot for consistency
    silence_threshold = int(sys.argv[3]) if len(sys.argv) == 4 else -40  # Optional argument

    if not os.path.isdir(folder):
        print(f"The directory {folder} does not exist.")
        sys.exit(1)

    concatenate_audios(folder, extension, silence_thresh=silence_threshold)
