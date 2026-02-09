# simple-python-audio-player

A simple Python script to play audio files from the command line.

## Features

- Play single audio files or all files in a directory
- Loop single files or all files indefinitely
- Supports MP3, WAV, OGG, FLAC, and M4A formats
- Scheduled playing with date/time configuration via JSON
- Simple command-line interface
- Appends a per-run play log (how many times each file was played)

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

### Play according to schedule:
```bash
python audio_player.py --schedule schedule.json
```

### Get help:
```bash
python audio_player.py --help
```

## Command-Line Arguments

- `path` - Path to audio file or directory containing audio files (required unless using --schedule)
- `--loop` - Loop a single audio file indefinitely
- `--loop-all` - Loop all audio files in a directory indefinitely
- `--log-file` - Append this run's play counts to the given log file (default: `play_log.txt`)
- `--schedule` - Path to JSON file containing schedule for playing audio files at specific times

## Supported Audio Formats

- MP3 (.mp3)
- WAV (.wav)
- OGG (.ogg)
- FLAC (.flac)
- M4A (.m4a)

## Scheduled Playing

The scheduled playing feature allows you to automatically play audio files at specific dates and times. This is useful for creating automated playlists, alarms, or timed announcements.

### Schedule File Format

Create a JSON file with the following structure:

```json
{
  "schedules": [
    {
      "start_time": "2026-02-09 18:00:00",
      "stop_time": "2026-02-09 20:00:00",
      "path": "/path/to/audio/file_or_directory"
    },
    {
      "start_time": "2026-02-10 08:00:00",
      "stop_time": "2026-02-10 10:00:00",
      "path": "/path/to/morning/music"
    }
  ]
}
```

Each schedule entry must include:
- `start_time`: When to start playing (ISO format: YYYY-MM-DD HH:MM:SS)
- `stop_time`: When to stop playing (ISO format: YYYY-MM-DD HH:MM:SS)
- `path`: Path to audio file or directory to play

### How It Works

1. The player monitors the current time and checks against all schedules
2. When the current time falls within a schedule's start/stop window, it begins playing
3. Audio files from the specified path will loop continuously until the stop time
4. If multiple schedules overlap, the first matching schedule takes priority
5. When a schedule ends, playback stops automatically

### Example Usage

See `schedule_example.json` for a complete example. Run with:

```bash
python audio_player.py --schedule schedule_example.json
```

The player will remain running and automatically start/stop playback according to the schedule. Press Ctrl+C to exit.

### M4A support notes (Windows)

`pygame`/SDL_mixer **may not** be able to decode `.m4a` (AAC) on some systems. If you see errors like `pygame.error: ModPlug_Load failed`, this project will try a best-effort fallback using **FFmpeg's** `ffplay` (if installed and available on `PATH`).

If M4A playback fails:
- Install FFmpeg and ensure `ffplay` is on `PATH`, or
- Convert the file to `.ogg` or `.wav`.

### Installing FFmpeg (for `ffplay`)

This project uses `ffplay` (included with FFmpeg) as an optional fallback player for `.m4a` files.

#### Windows 11

**Option 1: winget**

```bash
winget install --id Gyan.FFmpeg
```

Close and reopen your terminal, then verify:

```bash
ffplay -version
```

**Option 2: manual download**

1. Download a Windows FFmpeg build: https://www.gyan.dev/ffmpeg/builds/
2. Extract it (for example to `C:\ffmpeg`)
3. Add `C:\ffmpeg\bin` to your `PATH`
4. Verify:

```bash
where ffplay
ffplay -version
```

#### macOS

Using Homebrew:

```bash
brew install ffmpeg
```

Verify:

```bash
which ffplay
ffplay -version
```

#### Linux

**Debian/Ubuntu:**

```bash
sudo apt update
sudo apt install ffmpeg
```

**Fedora:**

```bash
sudo dnf install ffmpeg
```

**Arch:**

```bash
sudo pacman -S ffmpeg
```

Verify:

```bash
which ffplay
ffplay -version
```

## Requirements

- Python 3.6+
- pygame 2.0.0+

## License

This project is open source and available under the MIT License.

## Play log

After each run, the script appends a new entry to `play_log.txt` (or the file provided via `--log-file`) including:
- Run start/end timestamps
- Total plays during the run
- Plays per file during the run