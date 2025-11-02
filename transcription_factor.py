import os
import json
import argparse
import time
from faster_whisper import WhisperModel

# --- Configuration file path ---
CONFIG_FILE = "settings.conf"

def load_config():
    """Load configuration from settings.conf or create defaults"""
    defaults = {
        "video_folder": ".",
        "output_folder": ".",
        "model_size": "base.en",
        "file_types": [".mp4", ".mkv"],
        "beam_size": 5,
        "device": "auto"
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                return {**defaults, **config}  # Merge with defaults
        except Exception as e:
            print(f"Error reading {CONFIG_FILE}: {e}. Using defaults.")
            return defaults
    else:
        # Create default config file
        save_config(defaults)
        return defaults

def save_config(config):
    """Save configuration to settings.conf"""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        print(f"✓ Settings saved to {CONFIG_FILE}")
    except Exception as e:
        print(f"Error saving {CONFIG_FILE}: {e}")

def format_timestamp(seconds):
    """Converts seconds to SRT timestamp format (HH:MM:SS,ms)"""
    milliseconds = int((seconds - int(seconds)) * 1000)
    t = time.gmtime(seconds)
    return f"{t.tm_hour:02}:{t.tm_min:02}:{t.tm_sec:02},{milliseconds:03}"

def generate_transcript(video_folder, output_folder, model_size, file_types, beam_size, device):
    """
    Primary function for running transcription on all video files in the specified folder.
    """
    print(f"Loading Whisper model '{model_size}'...")
    
    # Validate folders
    if not os.path.exists(video_folder):
        print(f"Error: Video folder '{video_folder}' does not exist.")
        return
    
    if not os.path.exists(output_folder):
        try:
            os.makedirs(output_folder)
            print(f"Created output folder: {output_folder}")
        except Exception as e:
            print(f"Error creating output folder: {e}")
            return
    
    # Determine device
    if device == "auto":
        try:
            model = WhisperModel(model_size, device="cuda", compute_type="float16")
            print("GPU detected. Using CUDA.")
            actual_device = "cuda"
        except Exception as e:
            print(f"GPU not found or CUDA error: {e}. Falling back to CPU.")
            model = WhisperModel(model_size, device="cpu", compute_type="int8")
            actual_device = "cpu"
    else:
        try:
            model = WhisperModel(model_size, device=device, compute_type="float16" if device == "cuda" else "int8")
            print(f"Using {device.upper()} device.")
            actual_device = device
        except Exception as e:
            print(f"Error loading model on {device}: {e}. Falling back to CPU.")
            model = WhisperModel(model_size, device="cpu", compute_type="int8")
            actual_device = "cpu"

    # Convert file_types to lowercase for comparison
    file_types_lower = [ft.lower() for ft in file_types]
    
    # Find all video files with specified extensions
    video_files = [
        f for f in os.listdir(video_folder) 
        if os.path.splitext(f)[1].lower() in file_types_lower
    ]

    if not video_files:
        print(f"No video files found with types {file_types} in: {os.path.abspath(video_folder)}")
        return

    print(f"Found {len(video_files)} video file(s) to process.")
    print(f"Supported file types: {', '.join(file_types)}\n")

    for idx, filename in enumerate(video_files, 1):
        video_path = os.path.join(video_folder, filename)
        srt_filename = os.path.splitext(filename)[0] + ".srt"
        srt_path = os.path.join(output_folder, srt_filename)

        print(f"\n[{idx}/{len(video_files)}] --- Processing: {filename} ---")
        start_time = time.time()

        # Transcribe the audio with progress feedback
        print("Transcribing audio...")
        segments, info = model.transcribe(video_path, beam_size=beam_size)
        
        print(f"Detected language '{info.language}' with probability {info.language_probability:.2f}")
        
        # Process segments and write SRT with progress indication
        with open(srt_path, "w", encoding="utf-8") as srt_file:
            segment_count = 0
            for segment in segments:
                start = format_timestamp(segment.start)
                end = format_timestamp(segment.end)
                text = segment.text.strip()
                
                segment_count += 1
                srt_file.write(f"{segment_count}\n")
                srt_file.write(f"{start} --> {end}\n")
                srt_file.write(f"{text}\n\n")
                
                # Print progress indicator
                if segment_count % 10 == 0:
                    print(f"Processed {segment_count} segments...", end='\r')
            
            print(f"\nCompleted! Total segments: {segment_count}")

        end_time = time.time()
        print(f"Transcript saved to: {srt_path}")
        print(f"Time taken: {end_time - start_time:.2f} seconds")

def main():
    parser = argparse.ArgumentParser(
        description="Transcribe MP4/MKV videos to SRT files using Whisper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python transcription_factor.py
  python transcription_factor.py --input ./videos --output ./subtitles --model base.en
  python transcription_factor.py --model small.en
  python transcription_factor.py --filetypes .mp4 .mkv .avi
  python transcription_factor.py --input ./videos --filetypes .mkv
        """
    )
    
    parser.add_argument("--input", type=str, help="Input folder containing video files")
    parser.add_argument("--output", type=str, help="Output folder for SRT files")
    parser.add_argument("--model", type=str, help="Whisper model size (tiny.en, base.en, small.en, medium.en, large-v3)")
    parser.add_argument("--filetypes", nargs="+", type=str, help="Video file types to process (e.g., .mp4 .mkv .avi)")
    parser.add_argument("--beam-size", type=int, help="Beam size for transcription (default: 5)")
    parser.add_argument("--device", type=str, choices=["auto", "cuda", "cpu"], help="Device to use (auto, cuda, cpu)")
    
    args = parser.parse_args()
    
    # Load existing config
    config = load_config()
    
    # Override with command-line arguments if provided
    if args.input:
        config["video_folder"] = args.input
    if args.output:
        config["output_folder"] = args.output
    if args.model:
        config["model_size"] = args.model
    if args.filetypes:
        config["file_types"] = args.filetypes
    if args.beam_size:
        config["beam_size"] = args.beam_size
    if args.device:
        config["device"] = args.device
    
    # Save updated config
    save_config(config)
    
    # Display current settings
    print("\n" + "="*50)
    print("Current Settings:")
    print(f"  Input Folder:   {config['video_folder']}")
    print(f"  Output Folder:  {config['output_folder']}")
    print(f"  Model Size:     {config['model_size']}")
    print(f"  File Types:     {', '.join(config['file_types'])}")
    print(f"  Beam Size:      {config['beam_size']}")
    print(f"  Device:         {config['device']}")
    print("="*50 + "\n")
    
    # Run transcription
    generate_transcript(
        config["video_folder"],
        config["output_folder"],
        config["model_size"],
        config["file_types"],
        config["beam_size"],
        config["device"]
    )

def title():
    print(r"""

░▀█▀░█▀▄░█▀█░█▀█░█▀▀░█▀▀░█▀▄░▀█▀░█▀█░▀█▀░▀█▀░█▀█░█▀█░░░░░█▀▀░█▀█░█▀▀░▀█▀░█▀█░█▀▄
░░█░░█▀▄░█▀█░█░█░▀▀█░█░░░█▀▄░░█░░█▀▀░░█░░░█░░█░█░█░█░▄▄▄░█▀▀░█▀█░█░░░░█░░█░█░█▀▄
░░▀░░▀░▀░▀░▀░▀░▀░▀▀▀░▀▀▀░▀░▀░▀▀▀░▀░░░░▀░░▀▀▀░▀▀▀░▀░▀░░░░░▀░░░▀░▀░▀▀▀░░▀░░▀▀▀░▀░▀
-- Transcribe videos using Whisper --
    ~~ Leonardo Ferrisi, 2025 ~~
--------------------------------------------------------------------------------
""")
if __name__ == "__main__":
    title()
    main()