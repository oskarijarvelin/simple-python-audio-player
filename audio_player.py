#!/usr/bin/env python3
"""
Simple Python Audio Player
Plays audio files from a file or directory path with looping support.
"""

import argparse
import os
import sys
import pygame
import time
import subprocess
import json
import threading
from shutil import which
from collections import Counter
from datetime import datetime


class AudioPlayer:
    """Simple audio player class for playing audio files."""

    def __init__(self, log_file: str = 'play_log.txt'):
        """Initialize the audio player."""
        pygame.mixer.init()
        # Note: .m4a support via pygame depends on SDL_mixer codec support.
        # This script includes a best-effort Windows-friendly fallback for .m4a using ffplay (ffmpeg).
        self.supported_formats = ('.mp3', '.wav', '.ogg', '.flac', '.m4a')

        self.log_file = log_file
        self.play_counts = Counter()
        self.run_started_at = datetime.now()
        self.stop_flag = False
        self.playback_thread = None

        self._run_log_header_written = False

    def is_audio_file(self, filepath):
        """Check if a file is a supported audio format."""
        return filepath.lower().endswith(self.supported_formats)
    
    def get_audio_files(self, path):
        """Get list of audio files from a file or directory path."""
        audio_files = []
        
        if os.path.isfile(path):
            if self.is_audio_file(path):
                audio_files.append(path)
            else:
                print(f"Error: {path} is not a supported audio format.")
                print(f"Supported formats: {', '.join(self.supported_formats)}")
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in sorted(files):
                    filepath = os.path.join(root, file)
                    if self.is_audio_file(filepath):
                        audio_files.append(filepath)
        else:
            print(f"Error: {path} does not exist.")
        
        return audio_files

    def _play_with_ffplay(self, filepath: str, loop: bool = False) -> bool:
        """Play an audio file using ffplay (part of FFmpeg). Returns True if started successfully."""
        ffplay = which('ffplay')
        if not ffplay:
            return False

        # -nodisp: no window, -autoexit: quit when done, -loglevel error: keep output clean
        args = [ffplay, '-nodisp', '-autoexit', '-loglevel', 'error']
        if loop:
            # ffplay loops with -loop 0 (infinite)
            args += ['-loop', '0']
        args += [filepath]

        try:
            subprocess.run(args, check=True)
            return True
        except Exception:
            return False

    def _normalize_log_path(self, filepath: str) -> str:
        try:
            return os.path.abspath(filepath)
        except Exception:
            return filepath

    def _increment_play_count(self, filepath: str) -> None:
        self.play_counts[self._normalize_log_path(filepath)] += 1

    def _write_run_log_header_if_needed(self) -> None:
        if self._run_log_header_written:
            return
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write(f"Run start: {self.run_started_at.isoformat(sep=' ', timespec='seconds')}\n")
            self._run_log_header_written = True
        except Exception as e:
            print(f"Warning: failed to write play log header '{self.log_file}': {e}")

    def _append_log_line(self, line: str) -> None:
        self._write_run_log_header_if_needed()
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(line + "\n")
        except Exception as e:
            print(f"Warning: failed to write to play log '{self.log_file}': {e}")

    def _append_play_begin(self, filepath: str) -> None:
        ts = datetime.now().isoformat(sep=' ', timespec='seconds')
        self._append_log_line(f"PLAY_BEGIN {ts}  {self._normalize_log_path(filepath)}")

    def _append_play_event(self, filepath: str) -> None:
        """Append a single successful play event so the log updates as looping continues."""
        ts = datetime.now().isoformat(sep=' ', timespec='seconds')
        self._append_log_line(f"PLAY {ts}  {self._normalize_log_path(filepath)}")

    def _append_play_fail(self, filepath: str, reason: str) -> None:
        ts = datetime.now().isoformat(sep=' ', timespec='seconds')
        self._append_log_line(f"PLAY_FAIL {ts}  {self._normalize_log_path(filepath)}  {reason}")

    def play_file(self, filepath):
        """Play a single audio file."""
        self._append_play_begin(filepath)
        try:
            print(f"Playing: {filepath}")
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
            self._increment_play_count(filepath)
            self._append_play_event(filepath)

            # Wait for the music to finish playing
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        except pygame.error as e:
            # Common on Windows with .m4a when SDL_mixer lacks AAC/M4A codec support.
            if filepath.lower().endswith('.m4a'):
                print(f"pygame could not decode M4A ({e}). Trying ffplay fallback...")
                # Count as a play only if fallback succeeds
                if self._play_with_ffplay(filepath, loop=False):
                    self._increment_play_count(filepath)
                    self._append_play_event(filepath)
                    return
                self._append_play_fail(filepath, f"m4a_decode_failed:{e}")
                print("M4A playback failed.")
                print("To enable M4A on Windows, install FFmpeg (ffplay) and ensure 'ffplay' is on PATH,")
                print("or convert the file to .ogg/.wav.")
                return
            self._append_play_fail(filepath, f"pygame_error:{e}")
            print(f"Error playing {filepath}: {e}")
        except Exception as e:
            self._append_play_fail(filepath, f"error:{e}")
            print(f"Error playing {filepath}: {e}")

    def play(self, path, loop=False, loop_all=False):
        """
        Play audio files from the given path.

        Args:
            path: File or directory path
            loop: Loop a single file indefinitely
            loop_all: Loop all files indefinitely
        """
        audio_files = self.get_audio_files(path)

        if not audio_files:
            print("No audio files found.")
            return

        print(f"Found {len(audio_files)} audio file(s)")

        # Validate loop usage
        if loop and len(audio_files) > 1:
            print("Error: --loop can only be used with a single audio file.")
            print("Use --loop-all to loop multiple files.")
            return

        # Handle single file looping
        if len(audio_files) == 1 and loop:
            target = audio_files[0]
            print(f"Looping: {target}")
            print("Press Ctrl+C to stop")
            try:
                # To keep the play log updated, we loop by re-playing one iteration at a time,
                # which lets us increment counts and append a log line per iteration.
                while True:
                    self._append_play_begin(target)
                    if target.lower().endswith('.m4a'):
                        # Prefer ffplay if available; emulate looping by repeated single plays.
                        if self._play_with_ffplay(target, loop=False):
                            self._increment_play_count(target)
                            self._append_play_event(target)
                        else:
                            self._append_play_fail(target, "ffplay_not_available")
                            # Fall back to pygame single-play; may fail depending on codecs.
                            pygame.mixer.music.load(target)
                            pygame.mixer.music.play()
                            self._increment_play_count(target)
                            self._append_play_event(target)
                            while pygame.mixer.music.get_busy():
                                time.sleep(0.1)
                    else:
                        pygame.mixer.music.load(target)
                        pygame.mixer.music.play()
                        self._increment_play_count(target)
                        self._append_play_event(target)
                        while pygame.mixer.music.get_busy():
                            time.sleep(0.1)
            except KeyboardInterrupt:
                print("\nStopped by user")
                pygame.mixer.music.stop()
            except pygame.error as e:
                if target.lower().endswith('.m4a'):
                    print(f"M4A looping failed in pygame ({e}).")
                    print("Install FFmpeg (ffplay) and ensure 'ffplay' is on PATH, or convert to .ogg/.wav.")
                    return
                raise
        # Handle all files looping
        elif loop_all:
            print("Looping all files")
            print("Press Ctrl+C to stop")
            try:
                while True:
                    for audio_file in audio_files:
                        self.play_file(audio_file)
            except KeyboardInterrupt:
                print("\nStopped by user")
                pygame.mixer.music.stop()
        # Play all files once
        else:
            for audio_file in audio_files:
                self.play_file(audio_file)
            print("Playback finished")

    def write_run_log(self) -> None:
        """Append a run summary to the play log file."""
        ended_at = datetime.now()
        duration_s = int((ended_at - self.run_started_at).total_seconds())

        total = sum(self.play_counts.values())

        lines = []
        lines.append(f"Run end:   {ended_at.isoformat(sep=' ', timespec='seconds')}")
        lines.append(f"Duration:  {duration_s}s")
        lines.append(f"Total plays (this run): {total}")
        lines.append("Plays by file:")

        if not self.play_counts:
            lines.append("  (no plays)")
        else:
            for path, count in self.play_counts.most_common():
                lines.append(f"  {count}  {path}")

        lines.append("")

        self._write_run_log_header_if_needed()
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write("\n".join(lines))
        except Exception as e:
            print(f"Warning: failed to write play log '{self.log_file}': {e}")

def main():
    """Main entry point for the audio player."""
    parser = argparse.ArgumentParser(
        description='Simple Python Audio Player - Play audio files from file or directory path',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s song.mp3                    # Play a single file
  %(prog)s song.mp3 --loop             # Loop a single file
  %(prog)s /path/to/music              # Play all files in directory
  %(prog)s /path/to/music --loop-all   # Loop all files in directory
  %(prog)s --schedule schedule.json    # Play according to schedule file
        """
    )
    
    parser.add_argument(
        'path',
        nargs='?',
        help='Path to audio file or directory containing audio files'
    )
    
    parser.add_argument(
        '--loop',
        action='store_true',
        help='Loop a single audio file indefinitely'
    )
    
    parser.add_argument(
        '--loop-all',
        action='store_true',
        help='Loop all audio files indefinitely'
    )
    
    parser.add_argument(
        '--log-file',
        default='play_log.txt',
        help='Path to a log file where this run\'s play counts will be appended (default: play_log.txt)'
    )

    parser.add_argument(
        '--schedule',
        help='Path to JSON file containing schedule for playing audio files at specific times'
    )

    args = parser.parse_args()
    
    # Validate arguments
    if not args.schedule and not args.path:
        print("Error: path argument is required when not using --schedule")
        parser.print_help()
        sys.exit(1)
    
    # Create player
    player = AudioPlayer(log_file=args.log_file)
    
    try:
        # Handle scheduled mode
        if args.schedule:
            if not os.path.exists(args.schedule):
                print(f"Error: Schedule file '{args.schedule}' does not exist.")
                sys.exit(1)
            player.play_scheduled(args.schedule)
        else:
            # Validate path for regular play mode
            if not os.path.exists(args.path):
                print(f"Error: Path '{args.path}' does not exist.")
                sys.exit(1)
            player.play(args.path, loop=args.loop, loop_all=args.loop_all)
    finally:
        player.write_run_log()


if __name__ == '__main__':
    main()
