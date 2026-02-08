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


class AudioPlayer:
    """Simple audio player class for playing audio files."""
    
    def __init__(self):
        """Initialize the audio player."""
        pygame.mixer.init()
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
    
    def play_file(self, filepath):
        """Play a single audio file."""
        try:
            print(f"Playing: {filepath}")
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
            
            # Wait for the music to finish playing
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
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
            print(f"Looping: {audio_files[0]}")
            print("Press Ctrl+C to stop")
            try:
                pygame.mixer.music.load(audio_files[0])
                pygame.mixer.music.play(-1)  # -1 means loop indefinitely
                
                # Keep playing until interrupted
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopped by user")
                pygame.mixer.music.stop()
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
