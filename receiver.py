#!/usr/bin/env python3
"""
Sound Chat Receiver
Captures audio signals and converts them back to text messages.
Uses FSK (Frequency Shift Keying) demodulation for reliable reception.
"""

import numpy as np
import sounddevice as sd
import argparse
import time
import sys
from scipy import signal
from scipy.fft import fft, fftfreq

class SoundReceiver:
    def __init__(self, sample_rate=44100, bit_duration=0.1, timeout=30):
        """
        Initialize the sound receiver.
        
        Args:
            sample_rate (int): Audio sample rate in Hz
            bit_duration (float): Duration of each bit in seconds
            timeout (int): Recording timeout in seconds
        """
        self.sample_rate = sample_rate
        self.bit_duration = bit_duration
        self.timeout = timeout
        
        # FSK frequencies (must match sender)
        self.freq_0 = 1000  # Frequency for bit '0' (1kHz)
        self.freq_1 = 2000  # Frequency for bit '1' (2kHz)
        self.freq_start = 500   # Start tone (500Hz)
        self.freq_end = 3000    # End tone (3kHz)
        
        # Detection parameters
        self.freq_tolerance = 50  # Hz tolerance for frequency detection
        self.min_amplitude = 0.01  # Minimum amplitude threshold
        
        print(f"Sound Receiver initialized:")
        print(f"  Sample Rate: {self.sample_rate} Hz")
        print(f"  Bit Duration: {self.bit_duration} s")
        print(f"  Timeout: {self.timeout} s")
        print(f"  Frequency 0: {self.freq_0} Hz")
        print(f"  Frequency 1: {self.freq_1} Hz")
    
    def detect_dominant_frequency(self, audio_chunk):
        """Detect the dominant frequency in an audio chunk."""
        if len(audio_chunk) == 0:
            return 0
        
        # Apply window to reduce spectral leakage
        windowed = audio_chunk * np.hanning(len(audio_chunk))
        
        # Calculate FFT
        fft_data = fft(windowed)
        freqs = fftfreq(len(audio_chunk), 1/self.sample_rate)
        
        # Get magnitude spectrum (only positive frequencies)
        magnitude = np.abs(fft_data[:len(fft_data)//2])
        freqs = freqs[:len(freqs)//2]
        
        # Find peak frequency
        if np.max(magnitude) < self.min_amplitude:
            return 0  # No significant signal
        
        peak_idx = np.argmax(magnitude)
        dominant_freq = abs(freqs[peak_idx])
        
        return dominant_freq
    
    def classify_frequency(self, freq):
        """Classify frequency as start, end, 0, 1, or noise."""
        if abs(freq - self.freq_start) < self.freq_tolerance:
            return 'START'
        elif abs(freq - self.freq_end) < self.freq_tolerance:
            return 'END'
        elif abs(freq - self.freq_0) < self.freq_tolerance:
            return '0'
        elif abs(freq - self.freq_1) < self.freq_tolerance:
            return '1'
        else:
            return 'NOISE'
    
    def binary_to_text(self, binary_str):
        """Convert binary string to text."""
        if len(binary_str) % 8 != 0:
            print(f"Warning: Binary length {len(binary_str)} is not multiple of 8")
            # Pad with zeros if necessary
            binary_str = binary_str.ljust((len(binary_str) + 7) // 8 * 8, '0')
        
        text = ""
        for i in range(0, len(binary_str), 8):
            byte = binary_str[i:i+8]
            if len(byte) == 8:
                char_code = int(byte, 2)
                if 32 <= char_code <= 126:  # Printable ASCII
                    text += chr(char_code)
                else:
                    text += f"[{char_code}]"  # Non-printable characters
        
        return text
    
    def process_audio(self, audio_data):
        """Process recorded audio and extract message."""
        print(f"\nProcessing audio data: {len(audio_data)} samples")
        
        # Calculate samples per bit
        samples_per_bit = int(self.sample_rate * self.bit_duration)
        print(f"Samples per bit: {samples_per_bit}")
        
        # Split audio into chunks for analysis
        chunk_size = samples_per_bit
        chunks = []
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i+chunk_size]
            if len(chunk) >= chunk_size // 2:  # Keep chunks that are at least half full
                chunks.append(chunk)
        
        print(f"Created {len(chunks)} chunks for analysis")
        
        # Analyze each chunk
        classifications = []
        for i, chunk in enumerate(chunks):
            freq = self.detect_dominant_frequency(chunk)
            classification = self.classify_frequency(freq)
            classifications.append((freq, classification))
            
            if i < 20 or classification in ['START', 'END']:  # Show first 20 and important ones
                print(f"  Chunk {i}: {freq:.1f} Hz -> {classification}")
        
        # Find message boundaries
        start_idx = None
        end_idx = None
        
        for i, (freq, classification) in enumerate(classifications):
            if classification == 'START' and start_idx is None:
                start_idx = i
                print(f"\n📡 Found START signal at chunk {i}")
            elif classification == 'END' and start_idx is not None:
                end_idx = i
                print(f"📡 Found END signal at chunk {i}")
                break
        
        if start_idx is None:
            print("❌ No START signal found")
            return None
        
        if end_idx is None:
            print("⚠️  No END signal found, processing until end")
            end_idx = len(classifications)
        
        # Extract data bits (skip start signal and any silence)
        data_start = start_idx + 1
        # Skip potential silence chunk after start
        while (data_start < len(classifications) and 
               classifications[data_start][1] == 'NOISE'):
            data_start += 1
        
        data_end = end_idx
        # Skip potential silence chunk before end
        while (data_end > data_start and 
               classifications[data_end-1][1] == 'NOISE'):
            data_end -= 1
        
        print(f"Data chunks: {data_start} to {data_end-1}")
        
        # Convert data chunks to binary
        binary_data = ""
        for i in range(data_start, data_end):
            freq, classification = classifications[i]
            if classification in ['0', '1']:
                binary_data += classification
            elif classification == 'NOISE':
                print(f"  Warning: Noise at chunk {i} (freq: {freq:.1f} Hz)")
                # Try to make best guess based on frequency
                if abs(freq - self.freq_0) < abs(freq - self.freq_1):
                    binary_data += '0'
                    print(f"    Guessing '0'")
                else:
                    binary_data += '1'
                    print(f"    Guessing '1'")
        
        if not binary_data:
            print("❌ No data bits found")
            return None
        
        print(f"\nExtracted binary: {binary_data}")
        print(f"Binary length: {len(binary_data)} bits")
        
        # Convert binary to text
        try:
            message = self.binary_to_text(binary_data)
            return message
        except Exception as e:
            print(f"Error converting binary to text: {e}")
            return None
    
    def listen_for_message(self):
        """Listen for incoming audio message."""
        print(f"\n{'='*50}")
        print(f"LISTENING FOR MESSAGE...")
        print(f"{'='*50}")
        
        try:
            # Get available audio devices
            print(f"\nAvailable audio devices:")
            devices = sd.query_devices()
            print(devices)
            
            # Find default input device
            default_input = sd.default.device[0]
            print(f"\nUsing input device: {default_input}")
            
            print(f"\n🎤 Recording for {self.timeout} seconds...")
            print("Speak into your microphone or play sender.py from another device!")
            print("Press Ctrl+C to stop early")
            
            # Record audio
            audio_data = sd.rec(int(self.timeout * self.sample_rate), 
                              samplerate=self.sample_rate, 
                              channels=1, 
                              dtype=np.float32)
            sd.wait()  # Wait for recording to complete
            
            # Flatten audio data
            audio_data = audio_data.flatten()
            
            print(f"✅ Recording complete: {len(audio_data)} samples")
            print(f"Audio level: min={np.min(audio_data):.3f}, max={np.max(audio_data):.3f}")
            
            # Process the audio
            message = self.process_audio(audio_data)
            
            if message:
                print(f"\n🎉 MESSAGE RECEIVED: '{message}'")
                return message
            else:
                print(f"\n❌ No valid message found in audio")
                return None
                
        except KeyboardInterrupt:
            print(f"\n\n⏹️  Recording stopped by user")
            return None
        except Exception as e:
            print(f"❌ Error during recording: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description='Receive text messages via sound waves')
    parser.add_argument('--sample-rate', type=int, default=44100,
                       help='Audio sample rate (default: 44100)')
    parser.add_argument('--bit-duration', type=float, default=0.1,
                       help='Duration of each bit in seconds (default: 0.1)')
    parser.add_argument('--timeout', type=int, default=30,
                       help='Recording timeout in seconds (default: 30)')
    
    args = parser.parse_args()
    
    print("🎧 SOUND CHAT RECEIVER 🎧")
    print("=" * 30)
    
    receiver = SoundReceiver(
        sample_rate=args.sample_rate, 
        bit_duration=args.bit_duration,
        timeout=args.timeout
    )
    
    try:
        while True:
            message = receiver.listen_for_message()
            
            print(f"\n" + "="*50)
            if message:
                print(f"✅ SUCCESS: Received '{message}'")
            else:
                print(f"❌ FAILED: No message received")
            
            print("\nOptions:")
            print("  Press Enter to listen again")
            print("  Type 'quit' to exit")
            
            user_input = input(">>> ").strip().lower()
            if user_input == 'quit':
                break
                
    except KeyboardInterrupt:
        print(f"\n\n👋 Goodbye!")
    
    sys.exit(0)

if __name__ == "__main__":
    main()
