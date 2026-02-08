# simple-python-audio-player

A simple Python script to play audio files from the command line.

## Features

- Play single audio files or all files in a directory
- Loop single files or all files indefinitely
- Supports MP3, WAV, OGG, and FLAC formats
- Simple command-line interface

## Installation

1. Clone the repository:
```bash
git clone https://github.com/oskarijarvelin/simple-python-audio-player.git
cd simple-python-audio-player
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Play a single file:
```bash
python audio_player.py song.mp3
```

### Loop a single file:
```bash
python audio_player.py song.mp3 --loop
```

### Play all files in a directory:
```bash
python audio_player.py /path/to/music
```

### Loop all files in a directory:
```bash
python audio_player.py /path/to/music --loop-all
```

### Get help:
```bash
python audio_player.py --help
```

## Command-Line Arguments

- `path` - Path to audio file or directory containing audio files (required)
- `--loop` - Loop a single audio file indefinitely
- `--loop-all` - Loop all audio files in a directory indefinitely

## Supported Audio Formats

- MP3 (.mp3)
- WAV (.wav)
- OGG (.ogg)
- FLAC (.flac)

## Requirements

- Python 3.6+
- pygame 2.0.0+

## License

This project is open source and available under the MIT License.