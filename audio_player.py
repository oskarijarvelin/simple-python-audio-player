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
from shutil import which


class AudioPlayer:
    """Simple audio player class for playing audio files."""

    def __init__(self):
        """Initialize the audio player."""
        pygame.mixer.init()
        # Note: .m4a support via pygame depends on SDL_mixer codec support.
        # This script includes a best-effort Windows-friendly fallback for .m4a using ffplay (ffmpeg).
        self.supported_formats = ('.mp3', '.wav', '.ogg', '.flac', '.m4a')
    
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

    def play_file(self, filepath):
        """Play a single audio file."""
        try:
            print(f"Playing: {filepath}")
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()

            # Wait for the music to finish playing
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        except pygame.error as e:
            # Common on Windows with .m4a when SDL_mixer lacks AAC/M4A codec support.
            if filepath.lower().endswith('.m4a'):
                print(f"pygame could not decode M4A ({e}). Trying ffplay fallback...")
                if self._play_with_ffplay(filepath, loop=False):
                    return
                print("M4A playback failed.")
                print("To enable M4A on Windows, install FFmpeg (ffplay) and ensure 'ffplay' is on PATH,")
                print("or convert the file to .ogg/.wav.")
                return
            print(f"Error playing {filepath}: {e}")
        except Exception as e:
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
                if target.lower().endswith('.m4a'):
                    # pygame loop for M4A is often unsupported; prefer ffplay if available.
                    if self._play_with_ffplay(target, loop=True):
                        return
                    print("ffplay not available; attempting pygame loop (may fail if M4A codec not supported)...")
                pygame.mixer.music.load(target)
                pygame.mixer.music.play(-1)  # -1 means loop indefinitely

                # Keep playing until interrupted
                while True:
                    time.sleep(1)
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
        """
    )
    
    parser.add_argument(
        'path',
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
    
    args = parser.parse_args()
    
    # Validate path
    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' does not exist.")
        sys.exit(1)
    
    # Create and run player
    player = AudioPlayer()
    player.play(args.path, loop=args.loop, loop_all=args.loop_all)


if __name__ == '__main__':
    main()
