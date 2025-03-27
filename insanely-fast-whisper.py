#!/usr/bin/env python3

import click
import os
import time
import subprocess
import tempfile

@click.command()
@click.option('--model', default='openai/whisper-base', help='ASR model to use for speech recognition. Default is "openai/whisper-base". Model sizes include base, small, medium, large, large-v2. Additionally, try appending ".en" to model names for English-only applications (not available for large).')
@click.option('--device', default='cuda:0', help='Device to use for computation. Default is "cuda:0". If you want to use CPU, specify "cpu".')
@click.option('--dtype', default='float32', help='Data type for computation. Can be either "float32" or "float16". Default is "float32".')
@click.option('--batch-size', type=int, default=8, help='Batch size for processing. This is the number of audio files processed at once. Default is 8.')
@click.option('--better-transformer', is_flag=True, help='Flag to use BetterTransformer for processing. If set, BetterTransformer will be used.')
@click.option('--chunk-length', type=int, default=30, help='Length of audio chunks to process at once, in seconds. Default is 30 seconds.')
@click.argument('audio_file', type=str)
def asr_cli(model, device, dtype, batch_size, better_transformer, chunk_length, audio_file):
    from transformers import pipeline, AutoProcessor, AutoModelForSpeechSeq2Seq, WhisperProcessor, WhisperForConditionalGeneration
    import torch
    import numpy as np
    import librosa

    # Print device information
    click.echo(f"Device set to use {device}")
    
    # Initialize the model and processor separately for more control
    model_id = model
    torch_dtype = torch.float16 if dtype == "float16" else torch.float32
    
    # Load the processor and model using specific Whisper classes
    processor = WhisperProcessor.from_pretrained(model_id)
    asr_model = WhisperForConditionalGeneration.from_pretrained(
        model_id,
        torch_dtype=torch_dtype,
        low_cpu_mem_usage=True,
        use_safetensors=True
    )
    
    # Move model to the specified device
    asr_model = asr_model.to(device)
    
    if better_transformer:
        asr_model = asr_model.to_bettertransformer()
    
    # Create the pipeline with our custom model and processor
    pipe = pipeline(
        "automatic-speech-recognition",
        model=asr_model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        chunk_length_s=chunk_length,
        batch_size=batch_size,
        device=device
    )
    
    # Add a note about the attention mask warning
    click.echo("Note: The attention mask warning is a known issue with the Whisper model.")
    click.echo("We'll use a custom approach to handle timestamps properly.")

    # Perform ASR
    click.echo("Model loaded.")
    start_time = time.perf_counter()
    
    # Check if the file is a video and extract audio if needed
    audio_path = extract_audio_if_video(audio_file)
    
    # Process the audio file with the pipeline
    # The pipeline will handle chunking and timestamps
    def process_audio(audio_path):
        # Process the audio file with optimized parameters
        try:
            # Use the pipeline directly, but with optimized parameters
            # This will still show the warning but will work correctly
            result = pipe(
                audio_path,
                return_timestamps=True,
                generate_kwargs={
                    "language": "en",
                    "task": "transcribe",
                    "no_repeat_ngram_size": 3,  # Prevent repetition in output
                    "do_sample": False,  # Use greedy decoding for more reliable results
                }
            )
            return result
        except Exception as e:
            click.echo(f"Error in processing: {str(e)}")
            # Try a simpler approach if there's an error
            return pipe(
                audio_path,
                return_timestamps=True
            )
    
    # Process the audio file
    outputs = process_audio(audio_path)
    
    # Clean up temporary audio file if one was created
    if audio_path != audio_file and os.path.exists(audio_path):
        os.remove(audio_path)

    # Output the results
    click.echo(outputs)
    click.echo("Transcription complete.")
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    click.echo(f"ASR took {elapsed_time:.2f} seconds.")

    # Save ASR chunks to an SRT file
    audio_file_name = os.path.splitext(os.path.basename(audio_file))[0]
    srt_filename = f"{audio_file_name}.srt"
    with open(srt_filename, 'w', encoding="utf-8") as srt_file:
        prev = 0
        for index, chunk in enumerate(outputs['chunks']):
            prev, start_time = seconds_to_srt_time_format(prev, chunk['timestamp'][0])
            prev, end_time = seconds_to_srt_time_format(prev, chunk['timestamp'][1])
            srt_file.write(f"{index + 1}\n")
            srt_file.write(f"{start_time} --> {end_time}\n")
            srt_file.write(f"{chunk['text'].strip()}\n\n")

def extract_audio_if_video(file_path):
    """Extract audio from video file if the input is a video."""
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
    audio_extensions = ['.wav', '.mp3', '.flac', '.ogg', '.m4a']
    
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # If it's already an audio file, return the path as is
    if file_ext in audio_extensions:
        return file_path
    
    # If it's a video file, extract the audio
    if file_ext in video_extensions:
        click.echo(f"Extracting audio from video file: {file_path}")
        temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False).name
        
        try:
            # Use ffmpeg to extract audio
            cmd = [
                'ffmpeg',
                '-i', file_path,
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # PCM 16-bit little-endian format
                '-ar', '16000',  # 16kHz sample rate
                '-ac', '1',  # Mono
                '-y',  # Overwrite output file if it exists
                temp_audio
            ]
            
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            if process.returncode != 0:
                click.echo(f"Error extracting audio: {process.stderr.decode()}")
                return file_path  # Return original file if extraction fails
            
            click.echo("Audio extraction complete.")
            return temp_audio
            
        except Exception as e:
            click.echo(f"Error during audio extraction: {str(e)}")
            if os.path.exists(temp_audio):
                os.remove(temp_audio)
            return file_path
    
    # If it's neither a recognized video nor audio file, return the original path
    # and let the pipeline handle any errors
    return file_path

def seconds_to_srt_time_format(prev, seconds):
    if not (isinstance(seconds, int) or isinstance(seconds, float)):
        seconds = prev
    else:
        prev = seconds
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)
    return (prev, f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}")

if __name__ == '__main__':
    asr_cli()
