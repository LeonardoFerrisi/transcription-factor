# transcription-factor
A little program for transcribing videos

## Setup

# Setup

Using Python3+:

```bash
pip install -r requirements.txt
```

Make sure FFMPEG is installed. Follow instructions at https://ffmpeg.org/download.html or at https://www.geeksforgeeks.org/installation-guide/how-to-install-ffmpeg-on-windows/.

## Usage

#### Use saved settings
```bash
python transcription_factor.py
```

#### Process MKV files only
```bash
python transcription_factor.py --filetypes .mkv
```

#### Process multiple file types
```bash
python transcription_factor.py --filetypes .mp4 .mkv .avi
```

#### All parameters
```bash
python transcription_factor.py --input ./videos --output ./subs --model small.en --filetypes .mkv --beam-size 10
```

## Parameters

"video_folder": "./test",
    "output_folder": "./wah",
    "model_size": "base.en",
    "file_types": [
        ".mp4"
    ],
"beam_size": 5,
"device": "cuda"

### `input`

The local path to the folder containing video files to be transcribed.

### `output`

The local path to the folder where the transcription files will be saved.

### `model`

The size of the Whisper model to use for transcription. Options include:
- `tiny.en`
- `base.en`
- `small.en`
- `medium.en`
- `large-v3`

### `file_types`

A list of video file extensions to process. Examples:
- `.mp4`
- `.mkv`
- `.avi`

### `beam_size`

Beam size is a parameter used in the transcription process that controls the search algorithm's accuracy vs. speed tradeoff:

- Higher beam size (e.g., 10-15):
    - More thorough search through possible transcriptions
    - Better accuracy
    - Slower transcription
    - More memory usage

- Lower beam size (e.g., 1-5):
    - Faster transcription
    - Less accurate
    - Lower memory usage

Default value: `5` is a good balance for most use cases

### `device`

Device defines which hardware the transcription process will run on:

- `"auto"` (default):
    - Automatically detects if you have a GPU (CUDA)
    - Uses GPU if available, falls back to CPU if not
    - Best option for most users

- `"cuda"`:
    - Forces use of NVIDIA GPU
    - Much faster transcription (10-50x faster than CPU depending on GPU)
    - Requires NVIDIA graphics card and CUDA toolkit installed
    - Will error if CUDA isn't available

- `"cpu"`:
    - Forces use of CPU (processor)
    - Slower transcription
    - Works on any machine
    - Good for machines without GPU or for testing

# Authors
- LeonardoFerrisi, 2025