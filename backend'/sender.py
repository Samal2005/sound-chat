#!/usr/bin/env python3
"""
Sound Chat Sender
Converts text messages to audio signals and transmits them via speakers.
Uses FSK (Frequency Shift Keying) modulation for reliable transmission.
"""

import numpy as np
import sounddevice as sd
import argparse
import time
import sys

class SoundSender:
    def __init__(self, sample_rate=44100, bit_duration=0.1):
        """
        Initialize the sound sender.
        
        Args:
            sample_rate (int): Audio sample rate in Hz
            bit_duration (float): Duration of each bit in seconds
        """
        self.sample_rate = sample_rate
        self.bit_duration = bit_duration
        
        # FSK frequencies (well within human hearing range)
        self.freq_0 = 1000  # Frequency for bit '0' (1kHz)
        self.freq_1 = 2000  # Frequency for bit '1' (2kHz)
        self.freq_start = 500   # Start tone (500Hz)
        self.freq_end = 3000    # End tone (3kHz)
        
        print(f"Sound Sender initialized:")
        print(f"  Sample Rate: {self.sample_rate} Hz")
        print(f"  Bit Duration: {self.bit_duration} s")
        print(f"  Frequency 0: {self.freq_0} Hz")
        print(f"  Frequency 1: {self.freq_1} Hz")
    
    def text_to_binary(self, text):
        """Convert text to binary string."""
        binary = ''.join(format(ord(char), '08b') for char in text)
        print(f"Text '{text}' -> Binary: {binary}")
        return binary
    
    def generate_tone(self, frequency, duration):
        """Generate a sine wave tone."""
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        # Add slight fade in/out to reduce clicks
        tone = np.sin(2 * np.pi * frequency * t)
        fade_samples = min(100, samples // 10)
        if fade_samples > 0:
            tone[:fade_samples] *= np.linspace(0, 1, fade_samples)
            tone[-fade_samples:] *= np.linspace(1, 0, fade_samples)
        return tone
    
    def create_signal(self, text):
        """Create audio signal from text."""
        print(f"\nCreating audio signal for: '{text}'")
        
        # Convert text to binary
        binary_data = self.text_to_binary(text)
        
        # Create signal components
        signal_parts = []
        
        # Start tone (indicates beginning of transmission)
        print("Adding start tone...")
        start_tone = self.generate_tone(self.freq_start, 0.2)
        signal_parts.append(start_tone)
        
        # Add silence after start tone
        silence = np.zeros(int(self.sample_rate * 0.1))
        signal_parts.append(silence)
        
        # Convert each bit to corresponding frequency
        print(f"Encoding {len(binary_data)} bits...")
        for i, bit in enumerate(binary_data):
            freq = self.freq_1 if bit == '1' else self.freq_0
            tone = self.generate_tone(freq, self.bit_duration)
            signal_parts.append(tone)
            
            if (i + 1) % 8 == 0:  # Progress every byte
                print(f"  Encoded byte {(i + 1) // 8}/{len(binary_data) // 8}")
        
        # Add silence before end tone
        signal_parts.append(silence)
        
        # End tone (indicates end of transmission)
        print("Adding end tone...")
        end_tone = self.generate_tone(self.freq_end, 0.2)
        signal_parts.append(end_tone)
        
        # Combine all parts
        full_signal = np.concatenate(signal_parts)
        
        # Normalize to prevent clipping
        max_val = np.max(np.abs(full_signal))
        if max_val > 0:
            full_signal = full_signal / max_val * 0.8
        
        duration = len(full_signal) / self.sample_rate
        print(f"Signal created: {duration:.2f} seconds, {len(full_signal)} samples")
        
        return full_signal
    
    def send_message(self, text):
        """Send a text message via audio."""
        if not text.strip():
            print("Error: Cannot send empty message")
            return False
            
        print(f"\n{'='*50}")
        print(f"SENDING MESSAGE: '{text}'")
        print(f"{'='*50}")
        
        try:
            # Create the audio signal
            signal = self.create_signal(text)
            
            # Get available audio devices
            print(f"\nAvailable audio devices:")
            print(sd.query_devices())
            
            print(f"\nPlaying audio signal...")
            print("Make sure your speakers are on and receiver is listening!")
            print("Starting transmission in 3 seconds...")
            
            # Countdown
            for i in range(3, 0, -1):
                print(f"{i}...")
                time.sleep(1)
            
            # Play the signal
            print("🔊 TRANSMITTING NOW!")
            sd.play(signal, samplerate=self.sample_rate)
            sd.wait()  # Wait for playback to complete
            
            print("✅ Message sent successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Send text messages via sound waves')
    parser.add_argument('message', nargs='?', default='HELLO', 
                       help='Message to send (default: HELLO)')
    parser.add_argument('--sample-rate', type=int, default=44100,
                       help='Audio sample rate (default: 44100)')
    parser.add_argument('--bit-duration', type=float, default=0.1,
                       help='Duration of each bit in seconds (default: 0.1)')
    
    args = parser.parse_args()
    
    print("🎵 SOUND CHAT SENDER 🎵")
    print("=" * 30)
    
    sender = SoundSender(sample_rate=args.sample_rate, bit_duration=args.bit_duration)
    
    if args.message:
        success = sender.send_message(args.message)
        sys.exit(0 if success else 1)
    else:
        print("No message provided!")
        sys.exit(1)

if __name__ == "__main__":
    main()
