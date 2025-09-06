# 🎵 Sound Chat - Text Messages via Sound Waves

A Python project that enables two devices to exchange text messages using sound waves. Perfect for hackathons, demos, and exploring digital signal processing!

## 🚀 Quick Start

### 1. Setup Virtual Environment

```powershell
# Create virtual environment
python -m venv sound-chat-env

# Activate virtual environment
sound-chat-env\Scripts\Activate.ps1

# If you get execution policy errors, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Install Dependencies

```powershell
# Install all required packages
pip install -r requirements.txt
```

### 3. Test the System

**On Device 1 (Sender):**
```powershell
# Send "HELLO" message
python sender.py "HELLO"
```

**On Device 2 (Receiver):**
```powershell
# Start listening for messages
python receiver.py
```

## 📁 Project Structure

```
sound-chat/
├── sender.py          # Transmits text as sound waves
├── receiver.py        # Receives and decodes sound waves
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## 🔧 How It Works

### Technology: FSK (Frequency Shift Keying)
- **Bit '0'**: 1000 Hz tone
- **Bit '1'**: 2000 Hz tone
- **Start Signal**: 500 Hz tone
- **End Signal**: 3000 Hz tone

### Process
1. **Sender**: Text → Binary → Audio frequencies → Sound waves
2. **Receiver**: Sound waves → Frequency analysis → Binary → Text

## 📋 Detailed Usage

### Sender Options

```powershell
# Basic usage
python sender.py "YOUR MESSAGE"

# Custom parameters
python sender.py "HELLO WORLD" --sample-rate 44100 --bit-duration 0.1
```

**Parameters:**
- `message`: Text to send (required)
- `--sample-rate`: Audio sample rate (default: 44100 Hz)
- `--bit-duration`: Duration per bit in seconds (default: 0.1s)

### Receiver Options

```powershell
# Basic usage
python receiver.py

# Custom parameters
python receiver.py --timeout 60 --sample-rate 44100 --bit-duration 0.1
```

**Parameters:**
- `--timeout`: Recording timeout in seconds (default: 30s)
- `--sample-rate`: Audio sample rate (default: 44100 Hz)  
- `--bit-duration`: Duration per bit in seconds (default: 0.1s)

## 🎤 Hardware Setup

### For Same Computer Testing
1. **Use different audio devices** (if available)
2. **Use headphones + microphone** to prevent feedback
3. **Adjust volume** to medium level

### For Different Computers
1. **Position devices close** (1-3 feet apart)
2. **Use external speakers** for better transmission
3. **Minimize background noise**

## 🛠️ Troubleshooting

### Common Issues

#### 1. **Permission Errors**
```
PermissionError: [Errno 13] Permission denied
```
**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 2. **Microphone/Speaker Not Working**
```
OSError: No Default Input Device Available
```
**Solutions:**
- Check Windows audio settings
- Grant microphone permissions to Python
- Test with `python -c "import sounddevice; print(sounddevice.query_devices())"`

#### 3. **PyAudio Installation Issues**
```
ERROR: Microsoft Visual C++ 14.0 is required
```
**Solutions:**
```powershell
# Option 1: Install pre-compiled wheel
pip install pipwin
pipwin install pyaudio

# Option 2: Use conda instead
conda install pyaudio
```

#### 4. **No Message Received**
**Check:**
- Volume levels (not too low/high)
- Background noise
- Distance between devices
- Both devices using same parameters

#### 5. **Partial/Corrupted Messages**
**Solutions:**
- Increase bit duration: `--bit-duration 0.2`
- Reduce background noise
- Move devices closer
- Check audio device quality

### Audio Device Testing

```powershell
# Test audio devices
python -c "import sounddevice as sd; print(sd.query_devices()); sd.check_input_settings()"

# Test microphone
python -c "import sounddevice as sd; import numpy as np; print('Recording...'); data = sd.rec(2*44100, samplerate=44100, channels=1); sd.wait(); print(f'Max level: {np.max(np.abs(data))}')"
```

## 🎯 Demo Tips

### For Hackathon Presentations

1. **Test everything beforehand**
   ```powershell
   # Quick test sequence
   python sender.py "TEST" &
   timeout 5
   python receiver.py --timeout 10
   ```

2. **Prepare backup messages**
   ```powershell
   # Create test script
   echo 'python sender.py "HELLO HACKATHON"' > test.bat
   ```

3. **Use reliable hardware**
   - External USB microphone/speakers
   - Wired connections when possible

4. **Have multiple test messages ready**
   ```powershell
   python sender.py "DEMO"
   python sender.py "HELLO WORLD"
   python sender.py "SOUND CHAT WORKS"
   ```

### Performance Optimization

```powershell
# Faster transmission (shorter messages)
python sender.py "HI" --bit-duration 0.05

# More reliable transmission (longer messages)
python sender.py "HELLO" --bit-duration 0.2
```

## 🔍 Advanced Usage

### Custom Frequency Settings
Modify the frequency constants in both files:
```python
# In sender.py and receiver.py
self.freq_0 = 1000      # Frequency for bit '0'
self.freq_1 = 2000      # Frequency for bit '1'
self.freq_start = 500   # Start signal
self.freq_end = 3000    # End signal
```

### Multiple Device Communication
```powershell
# Device 1 → Device 2
python sender.py "MSG1"

# Device 2 → Device 1  
python sender.py "MSG2"

# Device 3 listening
python receiver.py
```

## 📊 Technical Specifications

- **Frequency Range**: 500-3000 Hz
- **Data Rate**: ~80 bits/second (default settings)
- **Character Encoding**: ASCII (8 bits per character)
- **Sample Rate**: 44.1 kHz
- **Transmission Range**: 1-10 meters (depending on environment)

## 🚨 Limitations

1. **Noise Sensitivity**: Background noise can interfere
2. **Range Limited**: Works best within a few meters
3. **ASCII Only**: Non-ASCII characters may not transmit correctly
4. **One-Way**: No built-in acknowledgment system

## 🔬 Extending the Project

### Ideas for Enhancement
1. **Error Correction**: Add checksums or parity bits
2. **Compression**: Implement text compression
3. **GUI Interface**: Create a user-friendly interface
4. **File Transfer**: Extend to send small files
5. **Two-Way Chat**: Implement full duplex communication

## 🆘 Getting Help

### If something doesn't work:

1. **Check this README** for common solutions
2. **Test each component separately**:
   ```powershell
   python -c "import numpy, scipy, sounddevice; print('All imports work!')"
   ```
3. **Verify audio hardware**:
   ```powershell
   python -c "import sounddevice as sd; sd.default.device = [0, 1]; print(sd.query_devices())"
   ```

### Contact Information
For hackathon support or questions, check the project repository or ask your mentors!

---

**Happy Hacking! 🎉**

*Built for hackathons with ❤️ - Ready to demo in minutes!*
